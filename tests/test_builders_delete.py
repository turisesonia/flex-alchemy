import pytest
import math

from sqlalchemy import inspect
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.orm.strategy_options import Load
from sqlalchemy.sql.dml import Delete
from sqlalchemy.sql.elements import (
    BinaryExpression,
    BooleanClauseList,
    UnaryExpression,
    Label,
    _textual_label_reference,
)
from sqlalchemy.sql.annotation import AnnotatedTable, AnnotatedColumn

from fluent_alchemy.builders.delete import DeleteBuilder
from fluent_alchemy.scopes.softdelete import SoftDeleteScope

from .models import Base, User


@pytest.fixture
def session() -> Session:
    return Base._session


@pytest.fixture
def builder(session: Session) -> DeleteBuilder:
    return DeleteBuilder(session, User())


def test_delete_builder_initial(builder: DeleteBuilder):
    assert isinstance(builder._model, User)
    assert builder._get_model_class() is User


def test_build_delete_stmt(builder: DeleteBuilder):
    stmt = builder._delete_stmt()

    assert isinstance(stmt, Delete)
    assert stmt.is_dml


def test_build_delete_stmt_with_single_where_clause(faker, builder: DeleteBuilder):
    builder.where(User.email == faker.email())
    stmt = builder._delete_stmt()

    assert isinstance(stmt.whereclause, BinaryExpression)
    assert stmt.whereclause.left.name == "email"


def test_build_delete_stmt_with_multiple_where_clause(faker, builder: DeleteBuilder):
    builder.where(User.email == faker.email()).where(User.state.is_(False))
    stmt = builder._delete_stmt()

    assert isinstance(stmt.whereclause, BooleanClauseList)

    validate_names = ["email", "state"]
    for idx, clause in enumerate(stmt.whereclause):
        assert isinstance(clause, BinaryExpression)
        assert clause.left.name == validate_names[idx]

    assert isinstance(stmt, Delete)
    assert stmt.is_dml


def test_build_delete_stmt_with_returning(builder: DeleteBuilder):
    builder.returning(User.id, User.email)

    stmt = builder._delete_stmt()

    assert len(stmt._returning) > 0

    validate_names = ["id", "email"]
    for idx, col in enumerate(stmt._returning):
        assert isinstance(col, AnnotatedColumn)
        assert col.name == validate_names[idx]


def test_build_delete_stmt_with_returning_all(builder: DeleteBuilder):
    builder.returning(User)

    stmt = builder._delete_stmt()

    assert len(stmt._returning) > 0

    for col in stmt._returning:
        assert isinstance(col, AnnotatedTable)
