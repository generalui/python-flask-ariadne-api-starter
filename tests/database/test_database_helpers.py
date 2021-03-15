import pytest
from sqlalchemy.orm import backref, joinedload
from sqlalchemy.dialects import postgresql
from api.database.database_helpers import (
    build_general_query, build_option_args, build_query_args)
from api.db_models import Base


@pytest.fixture(scope='module')
def MockModelClass(test_db):
    class RelatedMockModel(Base):
        __tablename__ = 'related_mock_models'
        id = test_db.Column(test_db.Integer, primary_key=True)
        name = test_db.Column(test_db.String, nullable=False)

        def __repr__(self):
            return '<RelatedMockModel %r>' % self.id

    class MockModel(Base):
        __tablename__ = 'mock_models'
        id = test_db.Column(test_db.Integer, primary_key=True)
        name = test_db.Column(test_db.String, nullable=False)
        relation_id = test_db.Column(test_db.Integer, test_db.ForeignKey(
            'related_mock_models.id'), nullable=False)

        relations = test_db.relationship(RelatedMockModel, backref=backref(
            'mock_models', uselist=True, lazy='noload'), uselist=False, lazy='noload')

        def __repr__(self):
            return '<MockModel %r>' % self.id
    return MockModel


def test_build_general_query(MockModelClass, test_db):
    query_arg_1 = 'id'
    query_arg_2 = 'name'
    accepted_query_args = [query_arg_1, query_arg_2]
    option_value_1 = 'relations'
    accepted_option_args = [option_value_1]
    test_1 = build_general_query(
        MockModelClass, args=[query_arg_1,
                              query_arg_2, option_value_1], accepted_option_args=accepted_option_args,
        accepted_query_args=accepted_query_args)
    test_2 = build_general_query(
        MockModelClass, args=[query_arg_1,
                              query_arg_2], accepted_option_args=accepted_option_args,
        accepted_query_args=accepted_query_args)
    test_3 = build_general_query(
        MockModelClass, args=[], accepted_option_args=accepted_option_args,
        accepted_query_args=accepted_query_args)

    assert str(test_1.statement.compile(dialect=postgresql.dialect())) == str(test_db.session.query(MockModelClass).options(
        joinedload(option_value_1)).statement.compile(dialect=postgresql.dialect()))

    assert str(test_2.statement.compile(dialect=postgresql.dialect())) == str(
        test_db.session.query(getattr(MockModelClass, query_arg_1), getattr(MockModelClass, query_arg_2)).statement.compile(dialect=postgresql.dialect()))

    assert str(test_3.statement.compile(dialect=postgresql.dialect())) == str(
        test_db.session.query(MockModelClass).statement.compile(dialect=postgresql.dialect()))


def test_build_option_args():
    expected_value_1 = 'nice'
    expected_value_2 = 'good'
    accepted_args = [expected_value_1, expected_value_2]
    test_1 = build_option_args(
        expected_value_1, accepted_args=accepted_args)
    test_2 = build_option_args(
        expected_value_1, expected_value_2, accepted_args=accepted_args)
    assert test_1 and isinstance(test_1, list)
    assert len(test_1) == 1
    assert test_2 and isinstance(test_2, list)
    assert len(test_2) == 2
    assert not build_option_args(expected_value_1)
    assert not build_option_args(expected_value_1, [])


def test_build_query_args(MockModelClass):
    arg_1 = 'id'
    arg_2 = 'name'
    accepted_args = [arg_1, arg_2]
    test_1 = build_query_args(MockModelClass, arg_1, arg_2,
                              accepted_args=accepted_args)
    test_2 = build_query_args(MockModelClass, arg_1, arg_2)
    test_3 = build_query_args(MockModelClass)
    assert test_1 == [MockModelClass.id, MockModelClass.name]
    assert test_2 == [MockModelClass]
    assert test_3 == [MockModelClass]
