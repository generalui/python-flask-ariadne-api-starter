from api import db
from api.db_models import User
from werkzeug.security import generate_password_hash
from psycopg2.errors import ForeignKeyViolation
from graphql import GraphQLError
from sqlalchemy.exc import IntegrityError
from .resolver_helpers import get_value
from api.constants.error_messages import INVALID_ADDRESS_ID

import datetime
import logging


def resolve_register_user(_, info, input):
    log = logging.getLogger('resolve_register_user')
    # The values in the passed input come from the GraphQL Schema. Translate them to Pythonic variables.
    clean_input = {
        'address_id': input.get('addressId'),
        'email': input.get('email'),
        'email_new': input.get('newEmail'),
        'first_name': input.get('firstName'),
        'last_name': input.get('firstName'),
        'password': input.get('password'),
        'password_new': input.get('newPassword'),
        'prefix': input.get('prefix'),
        'telephone': input.get('telephone')
    }

    try:
        session = db.session
        now = datetime.datetime.utcnow()
        password_hashed = generate_password_hash(clean_input['password'])
        new_password_hashed = generate_password_hash(
            clean_input['password_new']) if clean_input['password_new'] else None
        # Initial user status is "Pending" until they are fully registered.
        status = 'Pending'
        user = User(
            address_id=clean_input['address_id'],
            email=clean_input['email'],
            email_new=clean_input['email_new'],
            first_name=clean_input['first_name'],
            last_name=clean_input['last_name'],
            password=password_hashed,
            password_new=new_password_hashed,
            prefix=clean_input['prefix'],
            telephone=clean_input['telephone'],
            status=status
        )
        session.add(user)
        session.commit()
        return {
            'status': True,
            'id': user.id
        }
    except IntegrityError as err:
        errorInfo = err.orig.args
        log.info('IntegrityError %s', errorInfo[0])
        raise GraphQLError(message=INVALID_ADDRESS_ID)
