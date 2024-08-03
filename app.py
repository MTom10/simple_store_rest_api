import os
import secrets

import jwt
from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager

from db import db
from blocklist import BLOCKLIST
import models
from flask_migrate import Migrate

from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint


# function to create app
def create_app(db_url=None):
    # create flask  app, able to run the app, flask looks inside the folder for var called app
    app = Flask(__name__)

    # register blueprints with API
    # if there is exception in flask, let's see it
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    # standard for API doc
    app.config["OPENAPI_VERSION"] = "3.0.3"
    # where the route of API is
    app.config["OPENAPI_URL_PREFIX"] = "/"
    # doc config, use swagger for API documentation
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    # SQLAlchemy connection string through env variable, use env var if not sqlite
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # initialise flask SQLAlchemy extension and connect flask app to sqlalchemy
    db.init_app(app)

    # create tables if they don't exist and before first request
    with app.app_context():
        db.create_all()

    # has to be created after db.init_app, and we don't need sqlalchemy to create tables
    migrate = Migrate(app, db)

    # connect flask_smorest extension to flask app
    api = Api(app)

    # configure jwt and set a secret key, to check if token hasn't been forged, secrets.SystemRandom().getrandbits(128)
    # store it safely when deployed !
    app.config["JWT_SECRET_KEY"] = "33371376735479828244030811376210325553"
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token has been revoked", "error": "token_revoked"}
            ),
            401,
        )

    # function takes header and payload while there is a token to extract from
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "The token has expired", "error": "token_expired"}),
            401,
        )

    # function takes error parameter when there is no token to extract from
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token",
                    "error": "authorization_required",
                }
            ),
            401,
        )

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify (
                {
                    "description": "The token is nor fresh",
                    "error": "fresh_token_required",
                }
            ),
            401,
        )

    # register blueprints
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    return app
