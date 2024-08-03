from db import db


# configure items db
class ItemModel(db.Model):
    __tablename__ = "items"

    # declare columns
    id = db.Column(db.Integer, primary_key=True)
    # must have name
    name = db.Column(db.String(80), unique=False, nullable=False)
    description = db.Column(db.String)
    price = db.Column(db.Float(precision=2), unique=False, nullable=False)
    # store id is link between item table and store table, foreign key for mapping this to a different table.
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"), unique=False, nullable=False)
    # populate to allow the store to 'see' items easily
    store = db.relationship("StoreModel", back_populates="items")
    tags = db.relationship("TagModel", back_populates="items", secondary="items_tags")
