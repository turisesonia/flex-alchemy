import pytest

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql.dml import Insert
from sqlalchemy.sql.annotation import AnnotatedTable, AnnotatedColumn

from fluent_alchemy.builders.insert import InsertBuilder
from .models import Model, User


@pytest.fixture
def session() -> Session:
    return Model._session


@pytest.fixture
def builder(mocker) -> InsertBuilder:
    return InsertBuilder(mocker.Mock(), User())


def test_initial(builder: InsertBuilder):
    assert isinstance(builder._model, User)
    assert builder.get_model_class() is User


def test_set_values(faker, builder: InsertBuilder):
    values = {
        "name": faker.name(),
        "email": faker.email(),
        "password": faker.password(),
    }

    builder.values(**values).insert()

    stmt = builder._insert_stmt

    assert isinstance(stmt, Insert)
    assert stmt.is_dml

    for column, param in stmt._values.items():
        assert values[column.name] == param.value


def test_set_returning_all(faker, builder: InsertBuilder):
    values = {
        "name": faker.name(),
        "email": faker.email(),
        "password": faker.password(),
    }

    builder.values(values).returning(User).insert()

    #
    stmt = builder._insert_stmt
    builder._session.execute.assert_called_once_with(stmt)

    assert len(stmt._returning) > 0

    for col in stmt._returning:
        assert isinstance(col, AnnotatedTable)


def test_set_returning_specific_fields(faker, builder: InsertBuilder):
    values = {
        "name": faker.name(),
        "email": faker.email(),
        "password": faker.password(),
    }

    builder.values(values).returning(User.id, User.email).insert()

    stmt = builder._insert_stmt
    builder._session.execute.assert_called_once_with(stmt)

    assert len(stmt._returning) > 0

    validate_names = ["id", "email"]
    for idx, col in enumerate(stmt._returning):
        assert isinstance(col, AnnotatedColumn)
        assert col.name == validate_names[idx]


def test_set_execution_options(builder: InsertBuilder):
    builder.execution_options(render_nulls=True)

    stmt = builder._insert_stmt

    execution_options = stmt.get_execution_options()

    for key, value in execution_options.items():
        assert key == "render_nulls"
        assert value


def test_insert_multiple(faker, session: Session):
    count = faker.pyint(min_value=1, max_value=10)
    values = [
        {
            "name": faker.name(),
            "email": faker.email(),
            "password": faker.password(),
        }
        for _ in range(count)
    ]

    builder = InsertBuilder(session, User())
    builder.values(values).insert()

    with session() as db:
        users = db.scalars(select(User)).all()

        assert len(users) == count

        for idx, user in enumerate(users):
            assert user.name == values[idx]["name"]
            assert user.email == values[idx]["email"]
            assert user.password == values[idx]["password"]


def test_insert_single(faker, session: Session):
    values = {
        "name": faker.name(),
        "email": faker.email(),
        "password": faker.password(),
    }

    builder = InsertBuilder(session, User())
    builder.values(values).insert()

    with session() as db:
        user = db.scalars(select(User)).first()

        assert user.name == values["name"]
        assert user.email == values["email"]
        assert user.password == values["password"]
