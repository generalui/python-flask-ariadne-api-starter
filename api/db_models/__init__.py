from api import db

Base = db.Model

from .address import Address
from .user import User
