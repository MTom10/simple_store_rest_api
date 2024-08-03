import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models import StoreModel
from schemas import StoreSchema


# each blp needs unique name , simplest way is by creating __name__, and it goes into API documentation
blp = Blueprint("stores", __name__, description="Operations on stores")


# when request one of below requests from /stores endpoint it will go from here
@blp.route("/store/<int:store_id>")
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store

    # do not decorate delete function as it returns message only so far
    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return {"message": "Store deleted"}


# create the endpoint and the functions what returns the data, create store
@blp.route("/store")
class StoreList(MethodView):
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()

    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    # store_data goes in front of everything else if using arguments parameter !
    # when dealing with db marshmallow can turn object into JSON dict ! (SQLAlchemy for example)
    def post(self, store_data):
        store = StoreModel(**store_data)

        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(
                400,
                message="A store with than name already exists"
            )
        except SQLAlchemyError:
            abort(
                500,
                message="An error while creating the store"
            )
        return store
