import uuid

from asyncpg import UniqueViolationError
from sanic import Blueprint, response
from sanic.request import Request
from sanic.response import json
from sanic_openapi.openapi3 import openapi
from sanic_validation import validate_json

import settings
from users.auth import JWTAuthorization
from users.json_responses import (ActivateUserResponse200,
                                  ActivateUserResponse403,
                                  ActivateUserResponse404, LoginResponse200,
                                  LoginResponse401, RegisterResponse400,
                                  RegisterStatusCode201)
from users.json_validators import (LoginRequestBody, RegisterRequestBody,
                                   login_schema, register_schema)
from users.utils import (activate_user, create_user, create_user_verification,
                         filter_by_user_verification, get_user_by_username,
                         verify_hash)

users_blueprint = Blueprint("users", url_prefix="api/")


@openapi.summary("Create a new account")
@openapi.description(
    "Enter username and password you will be "
    "sent a link to activate your account"
)
@openapi.tag("Authentication")
@openapi.body(
    {"application/json": RegisterRequestBody},
    description=(
        "username length must not exceed 64 characters, "
        "password length must be between 8 and 64 characters"
    ),
    required=True,
)
@openapi.response(
    201, {"application/json": RegisterStatusCode201}, "Successful Response"
)
@openapi.response(
    400, {"application/json": RegisterResponse400}, "Bad Request Error"
)
@users_blueprint.route("/register", name="register", methods=("POST",))
@validate_json(register_schema)
async def register(request: Request) -> json:
    username = request.json.get("username")
    password = request.json.get("password")
    try:
        link = uuid.uuid4()
        database = request.app.config["database"]
        user_id = await create_user(database, username, password)
        await create_user_verification(database, link, user_id)
        request.ctx.session["user_data"] = (user_id, username)
        url = f"{settings.PROTOCOL}://{settings.HOST}/api/register/activate-user/{link}"

        return response.json(
            {"activation_link": url},
            status=201,
        )

    except UniqueViolationError:
        return response.json(
            {"error": "User with this username already exists"},
            status=400,
        )


@openapi.summary("Activate an account")
@openapi.description(
    "Activate an account using the link that was provided after registration"
)
@openapi.tag("Authentication")
@openapi.parameter("primary_key", uuid.UUID, location="path")
@openapi.response(
    200, {"application/json": ActivateUserResponse200}, "Successful Response"
)
@openapi.response(
    403, {"application/json": ActivateUserResponse403}, "Forbidden Error"
)
@openapi.response(
    404, {"application/json": ActivateUserResponse404}, "Not Found Error"
)
@users_blueprint.route(
    uri="register/activate-user/<primary_key:uuid>",
    name="activate-user",
    methods=("GET",),
)
async def activation(request: Request, primary_key: uuid.UUID) -> json:
    try:
        user_id, username = request.ctx.session["user_data"]
        database = request.app.config["database"]
        if await filter_by_user_verification(database, primary_key, user_id):
            await activate_user(database, user_id)
            token = await JWTAuthorization.user_authorize(
                request, user_id, username
            )

            return response.json(
                {"message": "Logged in successfully", "token": token},
                status=200,
            )
        else:
            return response.json(
                {"error": "It seems you have proceeded the wrong link :("},
                status=404,
            )
    except KeyError:
        return response.json(
            {"error": "Create an account, then follow the activation_link"},
            status=403,
        )


@openapi.summary("Login in account")
@openapi.description("Send your account data and login")
@openapi.tag("Authentication")
@openapi.body(
    {"application/json": LoginRequestBody},
    description="Enter your username and password",
    required=True,
)
@openapi.response(
    200, {"application/json": LoginResponse200}, "Successful Response"
)
@openapi.response(
    401, {"application/json": LoginResponse401}, "Unauthorized Error"
)
@users_blueprint.route("/login", methods=("POST",))
@validate_json(login_schema)
async def login(request: Request) -> json:
    username = request.json.get("username")
    password = request.json.get("password")
    database = request.app.config["database"]
    user = await get_user_by_username(database, username)
    if user and verify_hash(dict(user)["hashed_password"], password):
        token = await JWTAuthorization.user_authorize(
            request, dict(user)["id"], username
        )
        return response.json(
            {"message": "Logged in successfully", "token": token}, status=200
        )
    else:
        return response.json(
            {"error": "The username or password is entered incorrectly"},
            status=401,
        )
