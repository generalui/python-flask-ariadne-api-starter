from sqlalchemy import orm
from api import db
from . import Base
from api.enums import user_prefix_enum, user_status_enum


class User(Base):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String, nullable=False, index=True, unique=True)
    email_new = db.Column(db.String, nullable=True, index=True, unique=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String, nullable=False)
    password_new = db.Column(db.String, nullable=True)
    prefix = db.Column(user_prefix_enum, nullable=True)
    status = db.Column(user_status_enum, nullable=False, index=True)
    telephone = db.Column(db.String(50), nullable=True)

    address_id = db.Column(db.Integer, db.ForeignKey(
        'addresses.id'), nullable=True)

    address = db.relationship('Address', backref=orm.backref(
        'users', uselist=True, lazy='noload'), uselist=False, lazy='noload')

    created_at = db.Column(
        db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(
    ), server_onupdate=db.func.now())

    def __repr__(self):
        return '<User %r>' % self.id
