import pytest

from unittest.mock import MagicMock

from sqlalchemy.orm import Session
from sqlalchemy.sql.dml import Delete
from sqlalchemy.sql.elements import BinaryExpression, BooleanClauseList

from src.builders.delete import DeleteBuilder

from examples.models import User


@pytest.fixture
def session(mocker) -> MagicMock:
    return mocker.MagicMock(spec=Session)


@pytest.fixture
def builder(session) -> DeleteBuilder:
    return DeleteBuilder(User, session=session)


def test_builder_initial(builder: DeleteBuilder):
    assert builder._model is User


def test_build_stmt(builder: DeleteBuilder):
    stmt = builder._build()

    assert isinstance(stmt, Delete)
    assert stmt.is_dml


def test_build_stmt_with_single_where_clause(faker, builder: DeleteBuilder):
    email = faker.email()

    stmt = builder.where(User.email == email)._build()

    assert isinstance(stmt.whereclause, BinaryExpression)
    assert stmt.whereclause.left.name == "email"
    assert stmt.whereclause.right.value == email


def test_build_stmt_with_multiple_where_clause(faker, builder: DeleteBuilder):
    email = faker.email()
    created_at = faker.date_time()

    stmt = (
        builder.where(User.email == email).where(User.created_at == created_at)._build()
    )

    assert isinstance(stmt.whereclause, BooleanClauseList)

    assert len(stmt.whereclause) == 2

    validate = {"email": email, "created_at": created_at}

    for _, clause in enumerate(stmt.whereclause):
        assert isinstance(clause, BinaryExpression)
        assert validate[clause.left.name] == clause.right.value


def test_call_execute(faker, session, builder: DeleteBuilder):
    builder.where(User.email == faker.email()).execute(session=session)

    session.execute.assert_called_once()
    session.commit.assert_called_once()


def test_call_execute_with_not_commit(faker, session, builder: DeleteBuilder):
    builder.where(User.email == faker.email()).execute(session=session, commit=False)
    session.execute.assert_called_once()
    session.commit.assert_not_called()
