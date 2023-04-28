import pytest
from _pytest.monkeypatch import MonkeyPatch
from os import environ
from config import get_database_uri


@pytest.fixture(scope='module')
def TestingDB(app):
    return 'TestingDB'


@pytest.fixture(scope='module')
def TestingHost(app):
    return 'TestingHost'


@pytest.fixture(scope='module')
def TestingPassword(app):
    return 'TestingPassword'


@pytest.fixture(scope='module')
def TestingPort(app):
    return '4242'


@pytest.fixture(scope='module')
def TestingUser(app):
    return 'TestingUser'


def test_get_database_uri_non_test(
        TestingDB,
        TestingHost,
        TestingPassword,
        TestingPort,
        TestingUser,
        monkeypatch: MonkeyPatch):
    monkeypatch.setenv('POSTGRES_USER', TestingUser)
    monkeypatch.setenv('POSTGRES_PASSWORD', TestingPassword)
    monkeypatch.setenv('POSTGRES_DB', TestingDB)
    monkeypatch.setenv('POSTGRES_HOST', TestingHost)

    monkeypatch.delenv('POSTGRES_PORT', raising=False)
    assert get_database_uri(
    ) == f'postgresql://{TestingUser}:{TestingPassword}@{TestingHost}/{TestingDB}'

    monkeypatch.setenv('POSTGRES_PORT', TestingPort)
    assert get_database_uri(
    ) == f'postgresql://{TestingUser}:{TestingPassword}@{TestingHost}:{TestingPort}/{TestingDB}'


def test_get_database_uri_test(
        TestingDB,
        TestingHost,
        TestingPassword,
        TestingPort,
        TestingUser,
        monkeypatch: MonkeyPatch):
    monkeypatch.setenv('POSTGRES_USER_TEST', TestingUser)
    monkeypatch.setenv('POSTGRES_PASSWORD_TEST', TestingPassword)
    monkeypatch.setenv('POSTGRES_DB_TEST', TestingDB)
    monkeypatch.setenv('POSTGRES_HOST_TEST', TestingHost)

    monkeypatch.delenv('POSTGRES_PORT_TEST', raising=False)
    assert get_database_uri(
        test=True) == f'postgresql://{TestingUser}:{TestingPassword}@{TestingHost}/{TestingDB}'

    monkeypatch.setenv('POSTGRES_PORT_TEST', TestingPort)
    assert get_database_uri(
        test=True) == f'postgresql://{TestingUser}:{TestingPassword}@{TestingHost}:{TestingPort}/{TestingDB}'


def test_testing_config(app):
    FLASK_ENV = environ['FLASK_ENV']
    if FLASK_ENV == 'development':
        assert app.config['DEBUG']
    else:
        assert not app.config['DEBUG']
    assert not app.config['PROFILE']
    assert app.config['TESTING']
    assert app.config['SQLALCHEMY_DATABASE_URI'] == get_database_uri(test=True)
    assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] == False


def test_development_config(monkeypatch: MonkeyPatch):
    from api import create_app

    FLASK_ENV = 'development'
    monkeypatch.setenv('FLASK_ENV', FLASK_ENV)
    app = create_app()
    assert app.config['DEBUG']
    assert app.config['PROFILE']
    assert not app.config['TESTING']
    assert app.config['SQLALCHEMY_DATABASE_URI'] == get_database_uri()
    assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] == False


def test_staging_config(monkeypatch: MonkeyPatch):
    from api import create_app

    FLASK_ENV = 'staging'
    monkeypatch.setenv('FLASK_ENV', FLASK_ENV)
    app = create_app()
    assert not app.config['DEBUG']
    assert not app.config['PROFILE']
    assert not app.config['TESTING']
    assert app.config['SQLALCHEMY_DATABASE_URI'] == get_database_uri()
    assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] == False


def test_production_config(monkeypatch: MonkeyPatch):
    from api import create_app

    FLASK_ENV = 'production'
    monkeypatch.setenv('FLASK_ENV', FLASK_ENV)
    app = create_app()
    assert not app.config['DEBUG']
    assert not app.config['PROFILE']
    assert not app.config['TESTING']
    assert app.config['SQLALCHEMY_DATABASE_URI'] == get_database_uri()
    assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] == False
