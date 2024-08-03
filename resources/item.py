from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import ItemModel
from schemas import ItemSchema, ItemUpdateSchema

# each blp needs unique name , simplest way is by creating __name__, and it goes into API documentation
blp = Blueprint("items", __name__, description="Operations on items")


# GET specific item, DELETE item, PUT new item
@blp.route("/item/<int:item_id>")
class Item(MethodView):
    # main success response
    @jwt_required()
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        # query attribute possible thanks to sqlalchemy and ItemModel
        # get item by primary key or abort if otherwise
        item = ItemModel.query.get_or_404(item_id)
        return item

    @jwt_required()
    def delete(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {"message": "Item deleted"}

    # the order of decorators matters ! nest response decorator deeper inside arguments decor
    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    # item_data goes in front of everything else if using arguments parameter !
    def put(self,item_data, item_id):
        item = ItemModel.query.get(item_id)
        if item:
            item.price = item_data["price"]
            item.name = item_data["name"]
        else:
            item = ItemModel(id=item_id, **item_data)

        db.session.add(item)
        db.session.commit()

        return item


# GET all items, POST new item
@blp.route("/item")
class ItemList(MethodView):
    # when receiving multiple items make instance ItemSchema(many=True)
    @jwt_required()
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()

    # marshmallow checks only incoming data
    # jwt_required - cant call this endpoint without valid token
    @jwt_required(fresh=True)
    @blp.arguments(ItemSchema)
    @blp.response(200, ItemSchema)
    # item_data in class constructor contains JSON file which validates the schema with user request
    def post(self, item_data):
        # if an item with name and store id already exists, abort
        item = ItemModel(**item_data)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error while inserting the item")

        return item
