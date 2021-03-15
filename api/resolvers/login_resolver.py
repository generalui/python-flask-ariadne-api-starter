from api import db
from datetime import datetime
from graphql import GraphQLError
from werkzeug.security import check_password_hash
from api.constants.error_messages import INVALID_PASSWORD, LOGIN_ERROR, USER_NOT_FOUND
from api.constants.values import LOGIN_LIFE
from api.database.encode_jwt import encode_jwt
from api.db_models import User
from .resolver_helpers import address_request_fields, build_user_graphql_response, build_users_query, get_requested, get_selection_set, get_value, user_request_fields


def resolver_login(_, info, input):
    # The values in the passed input come from the GraphQL Schema. Translate them to Pythonic variables.
    password = input.get('password')

    # Request fields within 'user'
    selection_set = get_selection_set(info=info, child_node='user')
    requested = get_requested(
        selection_set=selection_set, requested_field_mapping=user_request_fields)
    # Request the password from the database on the user's behalf.
    requested.add('password')

    address_requested = get_requested(
        selection_set=selection_set, requested_field_mapping=address_request_fields, child_node='address')

    query, _alias = build_users_query(requested, address_requested)
    user = query.one_or_none()
    if user is None:
        raise GraphQLError(message=USER_NOT_FOUND)

    valid_password = check_password_hash(
        get_value(user, 'password', default=''), password)

    if not valid_password:
        raise GraphQLError(message=INVALID_PASSWORD)

    try:
        # Create the JWT
        jwt = encode_jwt(user.id, life=LOGIN_LIFE)

        return {
            'token': jwt.decode('utf-8'),
            'user': build_user_graphql_response(user)
        }
    except Exception as err:
        return {'error': LOGIN_ERROR}
