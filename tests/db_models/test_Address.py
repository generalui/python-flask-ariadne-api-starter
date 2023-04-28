import pytest
from sqlalchemy import and_
from api.database import address_core_fields, return_address_query
from api.db_models import Address


@pytest.fixture(scope='function')
def test_address(db_session, address_1, address_2, city, country, state, zipcode):
    test_address = Address(
        address_1=address_1,
        address_2=address_2,
        city=city,
        country=country,
        state=state,
        zipcode=zipcode)
    db_session.add(test_address)
    db_session.commit()

    yield db_session.query(Address).filter(and_(Address.address_1 == address_1, Address.address_2 == address_2, Address.city == city, Address.state == state, Address.zipcode == zipcode)).one_or_none()


def test_Address(app, db_session, test_address, address_1, address_2, city, country, state, zipcode):
    query = return_address_query(address_core_fields)
    result = query.filter(
        and_(
            Address.address_1 == address_1,
            Address.address_2 == address_2,
            Address.city == city,
            Address.state == state,
            Address.zipcode == zipcode)).one_or_none()

    assert result.id == test_address.id
    assert result.address_1 == address_1
    assert result.address_2 == address_2
    assert result.city == city
    assert result.country == country
    assert result.state == state
    assert result.zipcode == zipcode
    assert repr(result) == '<Address %r>' % result.id
