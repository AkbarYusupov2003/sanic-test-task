username_validation = {
    "type": "string",
    "maxlength": 64,
    "required": True,
}

password_validation = {
    "type": "string",
    "minlength": 8,
    "maxlength": 64,
    "required": True,
}


register_schema = {
    "username": username_validation,
    "password": password_validation,
}

login_schema = {
    "username": username_validation,
    "password": password_validation,
}


class RegisterRequestBody:
    username = "unique username"
    password = "12345678"


class LoginRequestBody:
    username = "your username"
    password = "your password"
