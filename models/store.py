from db import db


# configure items db
class StoreModel(db.Model):
    __tablename__ = "stores"

    # declare columns
    id = db.Column(db.Integer, primary_key=True)
    # must have name
    name = db.Column(db.String(80), unique=True, nullable=False)
    # lazy - doesn't load the table content before request.
    # cascade to delete children when parent is deleted
    items = db.relationship("ItemModel", back_populates="store", lazy="dynamic", cascade="all, delete")
    # add relationship to tags model
    tags = db.relationship("TagModel", back_populates="store", lazy="dynamic")
