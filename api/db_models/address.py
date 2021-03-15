from sqlalchemy import orm
from api import db
from . import Base


class Address(Base):
    __tablename__ = 'addresses'

    id = db.Column(db.Integer, primary_key=True)

    address_1 = db.Column(db.String(150), nullable=False)
    address_2 = db.Column(db.String(150), nullable=True)
    city = db.Column(db.String(150), nullable=False)
    country = db.Column(db.String(30), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    zipcode = db.Column(db.String(10), nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __repr__(self):
        return '<Address %r>' % self.id
