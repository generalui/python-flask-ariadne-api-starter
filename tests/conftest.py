import pytest
from api import create_app, db


@pytest.fixture(autouse=True)
def enable_transactional_tests(db_session):
    """
    Automatically enable transactions for all tests, without importing any extra fixtures.
    """
    pass


@pytest.fixture(scope='session')
def app():
    app = create_app(test=True)
    app.test_request_context().push()
    db.create_all()

    yield app
    db.session.remove()


@pytest.fixture(scope='session')
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture(scope='session')
def test_db(app):
    from api import db
    yield db


@pytest.fixture(scope='session')
def email():
    return 'test_user@example.com'


@pytest.fixture(scope='session')
def first_name():
    return 'Charlie'


@pytest.fixture(scope='session')
def last_name():
    return 'Parker'


@pytest.fixture(scope='session')
def password():
    return 'qwerty'


@pytest.fixture(scope='session')
def status():
    return 'Active'


@pytest.fixture(scope='session')
def telephone():
    return '206-555-1234'


@pytest.fixture(scope='session')
def _db(test_db):
    yield test_db
    test_db.session.remove()


@pytest.fixture(scope='session')
def address_1():
    return '728 212th Pl SW'


@pytest.fixture(scope='session')
def address_2():
    return 'Room #2'


@pytest.fixture(scope='session')
def city():
    return 'Lynnwood'


@pytest.fixture(scope='session')
def country():
    return 'USA'


@pytest.fixture(scope='session')
def state():
    return 'WA'


@pytest.fixture(scope='session')
def zipcode():
    return '98036'
