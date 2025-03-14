import pytest

from sqlalchemy import insert, select
from sqlalchemy.orm import Session
from sqlalchemy.sql.dml import Update
from sqlalchemy.sql.elements import BinaryExpression, BooleanClauseList
from sqlalchemy.sql.annotation import AnnotatedTable, AnnotatedColumn

from src.builders.update import UpdateBuilder

from example.models import User


@pytest.fixture
def session(mocker):
    return mocker.MagicMock()


@pytest.fixture
def builder() -> UpdateBuilder:
    return UpdateBuilder(User)


@pytest.fixture
def values(faker) -> dict:
    return {
        "name": faker.name(),
        "email": faker.email(),
        "password": faker.password(),
    }


def test_initial(builder: UpdateBuilder):
    assert isinstance(builder._model(), User)


def test_build_stmt(builder: UpdateBuilder, values: dict):
    with pytest.raises(ValueError):
        stmt = builder._build()

    stmt = builder.values(**values)._build()

    assert isinstance(stmt, Update)
    assert stmt.is_dml

    stmt_keys = {column.name for column in stmt._values.keys()}
    stmt_values = {param.value for param in stmt._values.values()}

    assert stmt_keys == set(values.keys())
    assert stmt_values == set(values.values())


def test_build_stmt_with_single_where_clause(faker, builder: UpdateBuilder):
    new_name = faker.name()
    find_email = faker.email()

    stmt = builder.values(name=new_name).where(User.email == find_email)._build()

    assert isinstance(stmt.whereclause, BinaryExpression)

    assert stmt.whereclause.left.name == "email"
    assert stmt.whereclause.right.value == find_email


def test_build_stmt_with_multiple_where_clauses(faker, builder: UpdateBuilder):
    new_name = faker.name()
    find_email = faker.email()

    stmt = (
        builder.values(name=new_name)
        .where(User.email == find_email)
        .where(User.enable.is_(True))
        ._build()
    )
    assert isinstance(stmt.whereclause, BooleanClauseList)

    validate_names = ["email", "enable"]
    for idx, clause in enumerate(stmt.whereclause):
        assert isinstance(clause, BinaryExpression)
        assert clause.left.name == validate_names[idx]


def test_build_stmt_with_returning(faker, builder: UpdateBuilder):
    new_name = faker.name()

    stmt = builder.values(name=new_name).returning(User.id, User.email)._build()

    assert len(stmt._returning) > 0

    validate_names = ["id", "email"]
    for idx, col in enumerate(stmt._returning):
        assert isinstance(col, AnnotatedColumn)
        assert col.name == validate_names[idx]


def test_build_stmt_with_returning_all(faker, builder: UpdateBuilder):
    new_name = faker.name()

    stmt = builder.values(name=new_name).returning(User)._build()

    assert len(stmt._returning) > 0

    for col in stmt._returning:
        assert isinstance(col, AnnotatedTable)
