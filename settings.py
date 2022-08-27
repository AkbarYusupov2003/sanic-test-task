import os

from dotenv import load_dotenv

load_dotenv()

PROTOCOL = os.environ.get("PROTOCOL", "http")
HOST_IP = os.environ.get("BACKEND_IP", "127.0.0.1")
HOST_PORT = os.environ.get("BACKEND_PORT", "8000")
HOST = f"{HOST_IP}:{HOST_PORT}"

DEBUG = os.environ.get("DEBUG", "False")

LOGGER_SETTINGS = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)s - %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "default",
            "level": "DEBUG",
        },
    },
    "loggers": {
        "statistics": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        },
    },
    "root": {"level": "DEBUG", "handlers": ["console"]},
}

JWT_SECRET = os.environ.get("JWT_SECRET", "d3f73888-f725-41f2-ae33-df5bbaf99cbc")
SECRET_KEY = os.environ.get("SECRET_KEY", "8e06922f-b52e-4203-ba61-66d54594e49e")
private_key = os.environ.get("private_key", "Qsd@3fd")


REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT = os.environ.get("REDIS_PORT", "6379")

connection = "postgresql://{0}:{1}@{2}/{3}".format(
    os.environ.get("DATABASE_USER", "postgres"),
    os.environ.get("DATABASE_PASSWORD", "postgres"),
    os.environ.get("DATABASE_HOST", "127.0.0.1:5432"),
    os.environ.get("DATABASE_DB", "DimaTech"),
)

API_TERMS_OF_SERVICE = os.environ.get(
    "TERMS_OF_SERVICE_URL",
    "https://github.com/AkbarYusupov2003/sanic-test-task/blob/master/README.md",
)
API_CONTACT_EMAIL = os.environ.get(
    "CONTACT_EMAIL",
    "admin@admin.com",
)
API_LICENSE_NAME = os.environ.get("LICENSE_NAME", "MIT")
API_LICENSE_URL = os.environ.get(
    "LICENSE_URL",
    "https://github.com/AkbarYusupov2003/sanic-test-task/blob/master/LICENSE",
)
print("JWT", JWT_SECRET)
try:
    from local_settings import *
except ImportError:
    pass
