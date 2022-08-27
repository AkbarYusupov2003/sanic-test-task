import binascii
import hashlib
import os
from uuid import UUID

from databases import Database

from users.models import user_verification, users


def generate_hash(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode("ascii")
    pwdhash = hashlib.pbkdf2_hmac(
        "sha512", password.encode("utf-8"), salt, 100000
    )
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode("ascii")


def verify_hash(stored_password, password):
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac(
        "sha512", password.encode("utf-8"), salt.encode("ascii"), 100000
    )
    pwdhash = binascii.hexlify(pwdhash).decode("ascii")
    return pwdhash == stored_password


# User model utils
async def create_user(database: Database, username: str, password: str) -> int:

    return await database.execute(
        query=users.insert(),
        values={
            "username": username,
            "hashed_password": generate_hash(password),
        },
    )


async def get_user_by_id(database: Database, user_id: int):
    query = "SELECT * FROM users WHERE id = :user_id"
    return await database.fetch_one(
        query=query,
        values={
            "user_id": user_id,
        },
    )


async def get_user_by_username(database: Database, username: str):
    query = "SELECT * FROM users WHERE username = :username"
    return await database.fetch_one(
        query=query,
        values={
            "username": username,
        },
    )


async def get_users_and_bills(database: Database):
    query = "SELECT * FROM users WHERE username = :username"
    return await database.execute(query=query)


async def is_user_admin(database: Database, user_id: int):
    query = "SELECT * FROM users WHERE id = :user_id AND is_admin = true AND is_active = true"
    return await database.fetch_one(query=query, values={"user_id": user_id})


async def is_user_active(database: Database, user_id: int):
    query = "SELECT * FROM users WHERE id = :user_id AND is_active = true"
    return await database.fetch_one(query=query, values={"user_id": user_id})


async def activate_user(database, user_id: int):
    query = "UPDATE users SET is_active = True WHERE id = :user_id"
    return await database.execute(
        query=query,
        values={
            "user_id": user_id,
        },
    )


async def change_user_activity(database, user_id: int, is_active: bool):
    query = "UPDATE users SET is_active = :is_active WHERE id = :user_id"
    return await database.execute(
        query=query, values={"user_id": user_id, "is_active": is_active}
    )


# UserVerification model utils
async def create_user_verification(
    database: Database, uuid: UUID, user_id: int
):

    return await database.execute(
        query=user_verification.insert(),
        values={
            "uuid": uuid,
            "user_id": user_id,
        },
    )


async def filter_by_user_verification(
    database: Database, uuid: UUID, user_id: int
):
    query = "SELECT * FROM user_verification WHERE uuid = :uuid AND user_id = :user_id"
    return await database.execute(
        query=query,
        values={
            "uuid": uuid,
            "user_id": user_id,
        },
    )
