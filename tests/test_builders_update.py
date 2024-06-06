import pytest

from sqlalchemy import insert, select
from sqlalchemy.orm import Session
from sqlalchemy.sql.dml import Update
from sqlalchemy.sql.elements import BinaryExpression, BooleanClauseList
from sqlalchemy.sql.annotation import AnnotatedTable, AnnotatedColumn

from fluent_alchemy.builders.update import UpdateBuilder

from .models import Model, User


@pytest.fixture
def session() -> Session:
    return Model._session


@pytest.fixture
def builder(mocker) -> UpdateBuilder:
    return UpdateBuilder(mocker.Mock(), User())


@pytest.fixture
def fake_user(faker) -> dict:
    return {
        "name": faker.name(),
        "email": faker.email(),
        "password": faker.password(),
    }


def test_update_builder_initial(builder: UpdateBuilder):
    assert isinstance(builder._model, User)
    assert builder.get_model_class() is User


def test_build_update_stmt(builder: UpdateBuilder):
    stmt = builder._update_stmt

    assert isinstance(stmt, Update)
    assert stmt.is_dml


def test_build_update_stmt_with_single_where_clause(
    faker, fake_user, builder: UpdateBuilder
):
    builder.values(fake_user).where(User.email == faker.email()).update()
    stmt = builder._update_stmt

    assert isinstance(stmt.whereclause, BinaryExpression)
    assert stmt.whereclause.left.name == "email"


def test_build_update_stmt_with_multiple_where_clauses(
    faker, fake_user, builder: UpdateBuilder
):
    builder.values(fake_user).where(User.email == faker.email()).where(
        User.state.is_(False)
    ).update()

    stmt = builder._update_stmt

    assert isinstance(stmt.whereclause, BooleanClauseList)

    validate_names = ["email", "state"]
    for idx, clause in enumerate(stmt.whereclause):
        assert isinstance(clause, BinaryExpression)
        assert clause.left.name == validate_names[idx]

    assert isinstance(stmt, Update)
    assert stmt.is_dml


def test_build_update_stmt_with_returning(fake_user, builder: UpdateBuilder):
    builder.values(fake_user).returning(User.id, User.email).update()

    stmt = builder._update_stmt

    assert len(stmt._returning) > 0

    validate_names = ["id", "email"]
    for idx, col in enumerate(stmt._returning):
        assert isinstance(col, AnnotatedColumn)
        assert col.name == validate_names[idx]


def test_build_update_stmt_with_returning_all(fake_user, builder: UpdateBuilder):
    builder.values(fake_user).returning(User).update()

    stmt = builder._update_stmt

    assert len(stmt._returning) > 0

    for col in stmt._returning:
        assert isinstance(col, AnnotatedTable)


def test_build_update_stmt_with_values(fake_user, builder: UpdateBuilder):
    builder.values(fake_user).update()

    stmt = builder._update_stmt

    for column, param in stmt._values.items():
        assert fake_user[column.name] == param.value


def test_update_without_where_clause(faker, fake_user, session: Session):
    # seed
    with session() as db:
        db.execute(
            insert(User).values(
                [
                    {
                        "name": faker.name(),
                        "email": faker.email(),
                        "password": faker.password(),
                    }
                    for _ in range(faker.pyint(min_value=1, max_value=10))
                ]
            )
        )
        db.commit()

    # update all
    UpdateBuilder(session, User()).values(name=fake_user["name"]).update()

    # validate
    with session() as db:
        users = db.scalars(select(User)).all()

        for user in users:
            assert user.name == fake_user["name"]
            assert user.email != fake_user["email"]
            assert user.password != fake_user["password"]


def test_update_with_where_clause(faker, fake_user, session: Session):
    target = {
        "name": faker.name(),
        "email": faker.email(),
        "password": faker.password(),
    }

    # seed
    with session() as db:
        values = [
            {
                "name": faker.name(),
                "email": faker.email(),
                "password": faker.password(),
            }
            for _ in range(faker.pyint(max_value=10))
        ]
        values.append(target)

        db.execute(insert(User).values(values))
        db.commit()

    # update with where clause
    UpdateBuilder(session, User()).where(User.email == target["email"]).values(
        name=fake_user["name"]
    ).update()

    # validate
    with session() as db:
        users = db.scalars(select(User)).all()

        for user in users:
            if user.email == target["email"]:
                assert user.name == fake_user["name"]
            else:
                assert user.name != fake_user["name"]
