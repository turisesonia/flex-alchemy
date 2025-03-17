import pytest

from sqlalchemy.orm import Session
from sqlalchemy.sql.dml import Insert
from sqlalchemy.sql.annotation import AnnotatedTable, AnnotatedColumn

from flex_alchemy.builders.insert import InsertBuilder
from examples.models import User

from flex_alchemy.exceptions import SessionNotProvidedError


@pytest.fixture
def session(mocker):
    return mocker.MagicMock(spec=Session)


@pytest.fixture
def builder(session) -> InsertBuilder:
    return InsertBuilder(User, session=session)


@pytest.fixture
def values(faker) -> dict:
    return {
        "name": faker.name(),
        "email": faker.email(),
        "password": faker.password(),
    }


def test_initial(builder: InsertBuilder):
    assert builder._model is User


def test_set_values(builder: InsertBuilder, values: dict):
    stmt = builder.values(**values)._build()

    assert isinstance(stmt, Insert)
    assert stmt.is_dml

    for column, param in stmt._values.items():
        assert values[column.name] == param.value


def test_set_returning_all(builder: InsertBuilder, values):
    stmt = builder.values(values).returning(User)._build()

    assert len(stmt._returning) > 0

    for col in stmt._returning:
        assert isinstance(col, AnnotatedTable)


def test_set_returning_specific_fields(builder: InsertBuilder, values):
    stmt = builder.values(values).returning(User.id, User.email)._build()

    assert len(stmt._returning) > 0

    validate_names = ["id", "email"]
    for idx, col in enumerate(stmt._returning):
        assert isinstance(col, AnnotatedColumn)
        assert col.name == validate_names[idx]


def test_set_execution_options(builder: InsertBuilder, values):
    stmt = builder.values(values).execution_options(render_nulls=True)._build()

    execution_options = stmt.get_execution_options()

    for key, value in execution_options.items():
        assert key == "render_nulls"
        assert value


def test_call_execute(session, builder: InsertBuilder, values: dict):
    builder.values(**values).execute(session=session)

    session.execute.assert_called_once()
    session.commit.assert_called_once()


def test_call_execute_not_commit(session, builder: InsertBuilder, values: dict):
    builder.values(**values).execute(session=session, commit=False)

    session.execute.assert_called_once()
    session.commit.assert_not_called()


def test_call_execute_without_session(faker, values: dict):
    builder = InsertBuilder(User)

    with pytest.raises(SessionNotProvidedError):
        builder.values(**values).execute()
