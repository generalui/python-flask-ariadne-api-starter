from api.db_models import User
from .database_helpers import build_general_query


user_related_fields = ['address']

user_core_fields = [
    'id',
    'address_id',
    'email',
    'email_new',
    'first_name',
    'last_name',
    'modified',
    'password',
    'password_new',
    'prefix',
    'status',
    'telephone',
    'created_at',
    'updated_at'
]


def return_user_query(*args, model=User):
    return build_general_query(
        model, args=args,
        accepted_option_args=user_related_fields,
        accepted_query_args=user_core_fields)
