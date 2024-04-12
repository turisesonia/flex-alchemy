import pytest


from sqlalchemy import inspect, insert
from sqlalchemy.engine.row import Row
from sqlalchemy.orm import scoped_session, joinedload
from sqlalchemy.orm.strategy_options import Load
from sqlalchemy.sql.elements import (
    BinaryExpression,
    UnaryExpression,
    Label,
    _textual_label_reference,
)
from sqlalchemy.sql.selectable import _OffsetLimitParam
from sqlalchemy.sql.annotation import AnnotatedColumn

from fluent_alchemy.builders.select import SelectBuilder

from .models import Base, User, Order


@pytest.fixture
def session() -> scoped_session:
    return Base._session


@pytest.fixture
def builder(session) -> SelectBuilder:
    return SelectBuilder(session, User())


def test_select_initial(builder: SelectBuilder):
    assert isinstance(builder._model, User)
    assert builder.get_model_class() is User


def test_select_all_fields(builder: SelectBuilder):
    columns = {col.name for col in inspect(User).columns}

    stmt = builder.select(User)._stmt

    assert stmt.is_select
    assert set(stmt.selected_columns.keys()) == columns


def test_select_specific_fields(builder: SelectBuilder):
    columns = {"id", "name", "email"}

    stmt = builder.select(User.id, User.name, User.email)._stmt

    assert stmt.is_select
    assert set(stmt.selected_columns.keys()) == columns


def test_select_where_clauses(faker, builder: SelectBuilder):
    name = faker.name()
    email = faker.email()

    validate = [
        {"field": "name", "value": name},
        {"field": "email", "value": email},
    ]

    stmt = builder.where(User.name == name).where(User.email == email)._stmt

    assert len(stmt.whereclause) == len(validate)

    for idx, clause in enumerate(stmt.whereclause):
        assert isinstance(clause, BinaryExpression)

        field = clause.left
        param = clause.right

        assert field.name == validate[idx]["field"]
        assert param.value == validate[idx]["value"]


def test_select_offset_clause(faker, builder: SelectBuilder):
    offset = faker.pyint()

    stmt = builder.offset(offset)._stmt

    assert stmt._offset == offset
    assert isinstance(stmt._offset_clause, _OffsetLimitParam)
    assert stmt._offset_clause.value == offset


def test_select_limit_clause(faker, builder: SelectBuilder):
    limit = faker.pyint()

    stmt = builder.limit(limit)._stmt

    assert stmt._limit == limit
    assert isinstance(stmt._limit_clause, _OffsetLimitParam)
    assert stmt._limit_clause is not None
    assert stmt._limit_clause.value == limit


def test_select_group_by_clause(session: scoped_session):
    stmt = SelectBuilder(session, User()).group_by(User.name)._stmt

    for clause in stmt._group_by_clause:
        assert isinstance(clause, AnnotatedColumn)

    stmt = SelectBuilder(session, User()).group_by(User.name.label("user_name"))._stmt

    for clause in stmt._group_by_clause:
        assert isinstance(clause, Label)

    stmt = SelectBuilder(session, User()).group_by("name")._stmt

    for clause in stmt._group_by_clause:
        assert isinstance(clause, _textual_label_reference)


def test_select_having_clause(session: scoped_session):
    stmt = (
        SelectBuilder(session, Order())
        .group_by(Order.state)
        .having(Order.price > 0)
        ._stmt
    )

    verifies = [AnnotatedColumn, BinaryExpression]

    for clause in stmt._group_by_clause:
        klass = verifies.pop(0)
        assert isinstance(clause, klass)

    stmt = SelectBuilder(session, Order()).having(Order.price > 0)._stmt

    assert len(stmt._group_by_clause) == 0


def test_select_order_by_clause(builder: SelectBuilder):
    stmt = builder.order_by(User.name.asc(), User.created_at.asc())._stmt

    assert len(stmt._order_by_clauses) == 2
    for clause in stmt._order_by_clauses:
        assert isinstance(clause, UnaryExpression)


def test_select_options_clause(builder: SelectBuilder):
    stmt = builder.options(joinedload(User.orders))._stmt

    for opt in stmt._with_options:
        assert isinstance(opt, Load)


def test_select_first(faker, session: scoped_session):
    name = faker.name()
    email = faker.email()

    session.add(User(name=name, email=email, password=faker.password()))
    session.commit()

    user = SelectBuilder(session, User()).where(User.email == email).first()
    assert isinstance(user, User)

    # specific fields
    user = (
        SelectBuilder(session, User())
        .select(User.name, User.email)
        .where(User.email == email)
        .first(partial_fields=True)
    )

    assert isinstance(user, Row)
    assert user.name == name
    assert user.email == email

    with pytest.raises(AttributeError):
        user.id


def test_select_get(faker, session: scoped_session):
    session.execute(
        insert(User).values(
            [
                {
                    "name": faker.name(),
                    "email": faker.email(),
                    "password": faker.password(),
                }
                for _ in range(5)
            ]
        )
    )
    session.commit()

    users = SelectBuilder(session, User()).select().get()
    assert len(users) == 5
    for user in users:
        assert isinstance(user, User)

    # specific fields
    users = (
        SelectBuilder(session, User())
        .select(User.name, User.email)
        .get(partial_fields=True)
    )

    assert len(users) == 5
    for user in users:
        assert isinstance(user, Row)

        with pytest.raises(AttributeError):
            user.id


def test_select_paginate(faker, session: scoped_session):
    session.execute(
        insert(User).values(
            [
                {
                    "name": faker.name(),
                    "email": faker.email(),
                    "password": faker.password(),
                    "state": True if i % 2 else False,
                }
                for i in range(50)
            ]
        )
    )
    session.commit()

    users = SelectBuilder(session, User()).select().where(User.state.is_(True)).get()

    users = (
        SelectBuilder(session, User())
        .select()
        # .where(User.state.is_(True))
        .options(joinedload(User.orders))
        .get()
        # SelectBuilder(session, User()).select().paginate()
    )

    # print(users)
    # print(users["total"], len(users["data"]))
