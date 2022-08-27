import datetime
import inspect
import json
import uuid
from functools import wraps
from typing import Optional

import jwt
import redis
from redis import ConnectionPool
from sanic import response

import settings
from users.utils import (generate_hash, get_user_by_id, is_user_active,
                         is_user_admin, verify_hash)


def login_required(insert_user=False):
    def decorator(func):
        @wraps(func)
        async def decorated_function(request, *args, **kwargs):

            user_id = await JWTAuthorization.get_id_if_authorized(request)
            database = request.app.config["database"]

            if await is_user_active(database, user_id):

                if insert_user:

                    user = await get_user_by_id(database, user_id=user_id)
                    res = func(request, user, *args, **kwargs)

                    if inspect.isawaitable(res):
                        return await res

                    return res

                return await func(request, *args, **kwargs)
            else:
                return response.json(
                    {
                        "error": "Login to your account to use this functionality"
                    },
                    status=401,
                )

        return decorated_function

    return decorator


def admin_rights_required():
    def decorator(func):
        @wraps(func)
        async def decorated_function(request, *args, **kwargs):

            user_id = await JWTAuthorization.get_id_if_authorized(request)
            database = request.app.config["database"]

            if await is_user_active(database, user_id):
                admin = await is_user_admin(database, user_id=user_id)
                if admin:
                    return await func(request, *args, **kwargs)
                else:
                    return response.json(
                        {
                            "error": "You don't have access to use this functionality"
                        },
                        status=403,
                    )
            else:
                return response.json(
                    {
                        "error": "Login to your account to use this functionality"
                    },
                    status=401,
                )

        return decorated_function

    return decorator


class JWTAuthorization:
    @staticmethod
    def _generate_token(
        redis_pool: ConnectionPool, user_id: int, username: str
    ) -> str:
        """Generate token and store it, return token_key"""

        conn = redis.Redis(connection_pool=redis_pool)
        token_key = str(uuid.uuid4())
        store_data = {
            "user_id": user_id,
            "token_hash": generate_hash(token_key),
        }
        conn.set(
            f"tokens_{username}",
            json.dumps(store_data),
            ex=datetime.timedelta(hours=24),
        )
        return token_key

    @staticmethod
    def _remove_token(redis_pool: ConnectionPool, username: str):
        """Remove token from storage"""

        conn = redis.Redis(connection_pool=redis_pool)
        conn.delete(username)

    @staticmethod
    def _get_jwt_data_from_request(request) -> Optional[dict]:
        """Return token from request"""
        authorization = request.headers.get("Authorization")
        if authorization:
            return jwt.decode(
                authorization[7:], settings.JWT_SECRET, algorithms=["HS256"]
            )

    @classmethod
    async def get_id_if_authorized(cls, request) -> Optional[int]:
        """Check if the user is authorized"""
        jwt_data = cls._get_jwt_data_from_request(request)
        redis_pool = request.app.config["redis_pool"]

        if not jwt_data:
            return False

        conn = redis.Redis(connection_pool=redis_pool)
        username = jwt_data["username"]
        store_data = json.loads(conn.get(f"tokens_{username}"))
        if not store_data:
            return False

        token_hash = store_data["token_hash"]

        if verify_hash(token_hash, jwt_data["token"]):
            return int(store_data["user_id"])

        return False

    @classmethod
    async def user_authorize(cls, request, user_id: int, username: str) -> str:
        """Authorize user"""
        redis_pool = request.app.config["redis_pool"]
        token = cls._generate_token(redis_pool, user_id, username)

        payload = {"username": username, "token": token}
        encoded_jwt = jwt.encode(
            payload, settings.JWT_SECRET, algorithm="HS256"
        )
        jwt_token = encoded_jwt.decode("UTF-8")
        return jwt_token

    @classmethod
    async def user_un_authorize(cls, request):
        """Un authorize user"""
        redis_pool = request.app.config["redis_pool"]
        jwt_data = cls._get_jwt_data_from_request(request)
        assert jwt_data

        cls._remove_token(redis_pool, jwt_data["username"])
