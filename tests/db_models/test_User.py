import pytest
from sqlalchemy import and_
from api.database import return_user_query, user_core_fields
from api.db_models import Address, User


@pytest.fixture(scope='function')
def test_address(db_session, address_1, address_2, city, country, state, zipcode):
    test_address = Address(address_1=address_1, address_2=address_2,
                           city=city, country=country, state=state, zipcode=zipcode)
    db_session.add(test_address)
    db_session.commit()

    yield db_session.query(Address).filter(
        and_(Address.address_1 == address_1, Address.address_2 == address_2, Address.city == city, Address.state == state, Address.zipcode == zipcode)).one_or_none()


@pytest.fixture(scope='function')
def test_user(db_session, test_address, email, first_name, last_name, password, status):
    user = User(
        address_id=test_address.id, email=email, first_name=first_name, last_name=last_name, password=password, status=status)
    db_session.add(user)
    db_session.commit()

    yield db_session.query(User).filter_by(email=email).one_or_none()


def test_User(app, db_session, test_address, test_user, email, first_name, last_name, password, status):
    query = return_user_query(user_core_fields)
    result = query.filter_by(email=email).one_or_none()
    assert result.id == test_user.id
    assert result.address_id == test_address.id
    assert result.email == email
    assert result.first_name == first_name
    assert result.last_name == last_name
    assert result.password == password
    assert result.status == status
    assert repr(result) == '<User %r>' % result.id


# def test_User_with_address(app, db_session, test_address, test_user, email, first_name, last_name, password, status):
#     query = return_user_query(user_related_fields)
#     result = query.filter_by(email=email).one_or_none()
#     assert result.id == test_user.id
#     assert result.address == test_address
#     assert result.address_id == test_address.id
#     assert result.email == email
#     assert result.first_name == first_name
#     assert result.last_name == last_name
#     assert result.password == password
#     assert result.status == status
#     assert repr(result) == '<User %r>' % result.id
