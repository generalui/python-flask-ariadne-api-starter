from api import db
from api.db_models import Address
import datetime


def resolve_add_address(_, info, input):
    # The values in the passed input come from the GraphQL Schema. Translate them to Pythonic variables.
    clean_input = {
        'country': input['country'],
        'address_1': input['address1'],
        'address_2': input['address2'],
        'city': input['city'],
        'state': input['state'],
        'zipcode': input['zipcode']
    }

    try:
        session = db.session
        now = datetime.datetime.utcnow()
        address = Address(
            country=clean_input['country'],
            address_1=clean_input['address_1'],
            address_2=clean_input['address_2'],
            city=clean_input['city'],
            state=clean_input['state'],
            zipcode=clean_input['zipcode']
        )
        session.add(address)
        session.commit()
        return {
            'status': True,
            'id': address.id
        }
    except ValidationError as err:
        return {
            'status': False
        }
