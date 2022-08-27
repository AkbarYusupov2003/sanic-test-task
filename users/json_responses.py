import settings


# Register
class RegisterStatusCode201:
    activation_link = f"{settings.PROTOCOL}://{settings.HOST}/api/register/activate-user/<uuid>"


class RegisterResponse400:
    error = "User with this username already exists"


class ActivateUserResponse200:
    message = "Logged in successfully"
    token = "jwt"


class ActivateUserResponse403:
    error = "Create an account, then follow the activation_link"


# Activate
class ActivateUserResponse404:
    error = "It seems you have proceeded the wrong link :("


# Login
class LoginResponse200:
    message = "Logged in successfully"
    token = "jwt"


class LoginResponse401:
    error = "The username or password is entered incorrectly"


# Unauthorized Error status_code=401
class UnauthorizedResponse401:
    error = "Login to your account to use this functionality"


# Admin Only
class NoAccessResponse403:
    error = "You don't have access to use this functionality"
