from _socket import gaierror
from databases import Database
from redis import ConnectionPool
from sanic import Sanic
from sanic_openapi import openapi3_blueprint
from sanic_session import Session
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeMeta

import settings

# dictConfig(settings.LOGGER_SETTINGS)

app = Sanic(__name__)


if not settings.SECRET_KEY:
    raise Exception("ERROR: SECRET_KEY is None")

app.config["SECRET_KEY"] = settings.SECRET_KEY

mainmetatadata: MetaData = MetaData()
Base: DeclarativeMeta = declarative_base(metadata=mainmetatadata)


@app.listener("before_server_start")
async def connect_db(app, loop):
    app.config["database"] = Database(
        app.config["CONNECTION"], force_rollback=app.config["FORCE_ROLLBACK"]
    )
    try:
        await app.config["database"].connect()

    except gaierror:
        raise gaierror(f"Can't connect to {app.config['CONNECTION']}")


@app.listener("before_server_stop")
async def disconnect_db(app, loop):
    await app.config["database"].disconnect()


def get_redis_pool(redis_db=0):
    return ConnectionPool(
        host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=redis_db
    )


def create_app(
    connection, run=True, force_rollback=False, redis_use=True, redis_db=0
):

    Session(app)

    app.config["redis_pool"] = get_redis_pool(redis_db) if redis_use else None
    app.config["CONNECTION"] = connection
    app.config["FORCE_ROLLBACK"] = force_rollback

    # TODO add real data

    app.config.API_TITLE = "Sanic-Store-OpenAPI"
    app.config.API_DESCRIPTION = "Authenticate, choose the appropriate product, pay for the product through one of your bills"
    app.config.API_TERMS_OF_SERVICE = settings.API_TERMS_OF_SERVICE
    app.config.API_CONTACT_EMAIL = settings.API_CONTACT_EMAIL
    app.config.API_LICENSE_NAME = settings.API_LICENSE_NAME
    app.config.API_LICENSE_URL = settings.API_LICENSE_URL

    app.blueprint(openapi3_blueprint)

    from admin.api import admin_blueprint
    from payment.api import payment_blueprint
    from products.api import products_blueprint
    from users.api import users_blueprint

    app.blueprint(users_blueprint)
    app.blueprint(products_blueprint)
    app.blueprint(payment_blueprint)
    app.blueprint(admin_blueprint)

    if run:
        app.run(
            settings.HOST_IP,
            int(settings.HOST_PORT),
            debug=bool(settings.DEBUG),
            auto_reload=bool(settings.DEBUG),
        )
    return app


if __name__ == "__main__":
    create_app(settings.connection)
