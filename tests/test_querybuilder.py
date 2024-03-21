import pytest

from sqlalchemy import inspect
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.orm.strategy_options import Load
from sqlalchemy.sql.elements import (
    BinaryExpression,
    UnaryExpression,
    Label,
    _textual_label_reference,
)
from sqlalchemy.sql.annotation import AnnotatedColumn

from sqlalchemy_model.builder import QueryBuilder
from sqlalchemy_model.scopes.softdelete import SoftDeleteScope
from .models import Base, User


@pytest.fixture
def session() -> Session:
    return Base._session


def test_builder_initial_value(session):
    builder = QueryBuilder(session, User())

    assert isinstance(builder._model, User)
    assert builder._get_model_class() is User


def test_build_select_stmt_with_all_columns(session):
    state = inspect(User)
    all_columns = {col.name for col in state.columns}

    builder = QueryBuilder(session, User())

    builder.select(User).where(User.email == "test@mail.com")

    stmt = builder._select_stmt()

    assert stmt.is_select

    select_columns = {col.name for col in stmt.selected_columns}

    assert len(builder._select_entities) > 0

    for entity in builder._select_entities:
        assert isinstance(entity, User.__class__)

    assert all_columns == select_columns


def test_build_select_stmt_with_specify_columns(session):
    from sqlalchemy.orm.attributes import InstrumentedAttribute

    builder = QueryBuilder(session, User())

    builder.select(User.name, User.email)

    stmt = builder._select_stmt()

    assert stmt.is_select

    select_columns = {col.name for col in stmt.selected_columns}

    assert len(builder._select_entities) == len(select_columns)

    for entity in builder._select_entities:
        assert isinstance(entity, InstrumentedAttribute)

    assert {"name", "email"} == select_columns


def test_build_select_stmt_with_where_clauses(faker, session):
    name = faker.name()
    email = faker.email()

    builder = (
        QueryBuilder(session, User())
        .where(User.name == name)
        .where(User.email == email)
        .where(User.state.is_(True))
    )

    stmt = builder._select_stmt()

    assert len(stmt.whereclause) == 3

    for clause in stmt.whereclause:
        assert isinstance(clause, BinaryExpression)


def test_build_select_stmt_with_offset_clause(faker, session):
    offset = faker.pyint()

    builder = QueryBuilder(session, User()).offset(offset)
    stmt = builder._select_stmt()

    assert stmt._offset_clause is not None
    assert stmt._offset == offset


def test_build_select_stmt_with_limit_clause(faker, session):
    limit = faker.pyint()

    builder = QueryBuilder(session, User()).limit(limit)
    stmt = builder._select_stmt()

    assert stmt._limit_clause is not None
    assert stmt._limit == limit


def test_build_select_stmt_with_group_by_clause(session):
    stmt = QueryBuilder(session, User()).group_by(User.state)._select_stmt()

    for clause in stmt._group_by_clause:
        assert isinstance(clause, AnnotatedColumn)

    stmt = (
        QueryBuilder(session, User())
        .group_by(User.name.label("user_name"))
        ._select_stmt()
    )

    for clause in stmt._group_by_clause:
        assert isinstance(clause, Label)

    stmt = QueryBuilder(session, User()).group_by("name")._select_stmt()

    for clause in stmt._group_by_clause:
        assert isinstance(clause, _textual_label_reference)


def test_build_select_stmt_with_order_by_clause(session):
    builder = QueryBuilder(session, User()).order_by(
        User.name.asc(), User.created_at.asc()
    )
    stmt = builder._select_stmt()

    for clause in stmt._order_by_clause:
        assert isinstance(clause, UnaryExpression)


def test_build_select_stmt_with_options(session):
    builder = QueryBuilder(session, User()).options(joinedload(User.orders))
    stmt = builder._select_stmt()

    for opt in stmt._with_options:
        assert isinstance(opt, Load)


def test_with_scope_boot(mocker, session: Session):
    mock_scope = mocker.Mock()

    QueryBuilder(session, User, {mock_scope.__class__: mock_scope})

    mock_scope.boot.assert_called_once()


def test_soft_delete_scope(mocker, session: Session):
    scopes = {SoftDeleteScope.__class__: SoftDeleteScope()}

    builder = QueryBuilder(session, User(), scopes)

    assert callable(builder._on_delete)
