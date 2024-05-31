import pytest

from sqlalchemy.orm import Session
from sqlalchemy.sql.dml import Update
from sqlalchemy.sql.elements import BinaryExpression, BooleanClauseList
from sqlalchemy.sql.annotation import AnnotatedTable, AnnotatedColumn

from fluent_alchemy.builders.update import UpdateBuilder

from .models import Base, User


@pytest.fixture
def session() -> Session:
    return Base._session


@pytest.fixture
def builder(session: Session) -> UpdateBuilder:
    return UpdateBuilder(session, User())


def test_update_builder_initial(builder: UpdateBuilder):
    assert isinstance(builder._model, User)
    assert builder.get_model_class() is User


def test_build_update_stmt(builder: UpdateBuilder):
    stmt = builder._update_stmt

    assert isinstance(stmt, Update)
    assert stmt.is_dml


def test_build_update_stmt_with_single_where_clause(faker, builder: UpdateBuilder):
    builder.where(User.email == faker.email())
    stmt = builder._update_stmt

    assert isinstance(stmt.whereclause, BinaryExpression)
    assert stmt.whereclause.left.name == "email"


def test_build_update_stmt_with_multiple_where_clauses(faker, builder: UpdateBuilder):
    builder.where(User.email == faker.email()).where(User.state.is_(False))
    stmt = builder._update_stmt

    assert isinstance(stmt.whereclause, BooleanClauseList)

    validate_names = ["email", "state"]
    for idx, clause in enumerate(stmt.whereclause):
        assert isinstance(clause, BinaryExpression)
        assert clause.left.name == validate_names[idx]

    assert isinstance(stmt, Update)
    assert stmt.is_dml


def test_build_update_stmt_with_returning(builder: UpdateBuilder):
    builder.returning(User.id, User.email)

    stmt = builder._update_stmt

    assert len(stmt._returning) > 0

    validate_names = ["id", "email"]
    for idx, col in enumerate(stmt._returning):
        assert isinstance(col, AnnotatedColumn)
        assert col.name == validate_names[idx]


def test_build_update_stmt_with_returning_all(builder: UpdateBuilder):
    builder.returning(User)

    stmt = builder._update_stmt

    assert len(stmt._returning) > 0

    for col in stmt._returning:
        assert isinstance(col, AnnotatedTable)


def test_build_update_stmt_with_values(faker, builder: UpdateBuilder):
    values = {
        "name": faker.name(),
        "email": faker.email(),
    }

    builder.values(**values)

    stmt = builder._update_stmt

    for column, param in stmt._values.items():
        assert values[column.name] == param.value


def test_update_execute(mocker, faker, session: Session, builder: UpdateBuilder):
    mock_execute = mocker.patch.object(session, "execute")
    mock_commit = mocker.patch.object(session, "commit")

    values = {
        "name": faker.name(),
        "email": faker.email(),
        "password": faker.password(),
    }

    builder.values(values)
    builder.execute()

    mock_execute.assert_called_once_with(builder._update_stmt)
    mock_commit.assert_called_once()
