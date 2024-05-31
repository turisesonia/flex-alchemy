import pytest

from sqlalchemy.orm import Session
from sqlalchemy.sql.dml import Insert
from sqlalchemy.sql.annotation import AnnotatedTable, AnnotatedColumn

from fluent_alchemy.builders.insert import InsertBuilder
from .models import Base, User


@pytest.fixture
def session() -> Session:
    return Base._session


@pytest.fixture
def builder(session: Session) -> InsertBuilder:
    return InsertBuilder(session, User())


def test_insert_initial(builder: InsertBuilder):
    assert isinstance(builder._model, User)
    assert builder.get_model_class() is User


def test_insert_values_stmt(faker, builder: InsertBuilder):
    values = {
        "name": faker.name(),
        "email": faker.email(),
        "password": faker.password(),
    }

    builder.values(**values)

    stmt = builder._insert_stmt

    assert isinstance(stmt, Insert)
    assert stmt.is_dml

    for column, param in stmt._values.items():
        assert values[column.name] == param.value


def test_insert_returning_all(builder: InsertBuilder):
    builder.returning(User)

    stmt = builder._insert_stmt

    assert len(stmt._returning) > 0

    for col in stmt._returning:
        assert isinstance(col, AnnotatedTable)


def test_insert_returning_specific_fields(builder: InsertBuilder):
    builder.returning(User.id, User.email)

    stmt = builder._insert_stmt

    assert len(stmt._returning) > 0

    validate_names = ["id", "email"]
    for idx, col in enumerate(stmt._returning):
        assert isinstance(col, AnnotatedColumn)
        assert col.name == validate_names[idx]


def test_insert_execution_options(builder: InsertBuilder):
    builder.execution_options(render_nulls=True)

    stmt = builder._insert_stmt

    execution_options = stmt.get_execution_options()

    for key, value in execution_options.items():
        assert key == "render_nulls"
        assert value


def test_insert_execute(mocker, faker, session: Session, builder: InsertBuilder):
    mock_execute = mocker.patch.object(session, "execute")
    mock_commit = mocker.patch.object(session, "commit")

    values = [
        {
            "name": faker.name(),
            "email": faker.email(),
            "password": faker.password(),
        },
        {
            "name": faker.name(),
            "email": faker.email(),
            "password": faker.password(),
        },
    ]

    builder.values(values)
    builder.execute()

    mock_execute.assert_called_once_with(builder._insert_stmt)
    mock_commit.assert_called_once()
