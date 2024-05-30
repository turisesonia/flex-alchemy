import pytest

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql.dml import Delete
from sqlalchemy.sql.elements import BinaryExpression, BooleanClauseList
from sqlalchemy.sql.annotation import AnnotatedTable, AnnotatedColumn

from fluent_alchemy.builders.delete import DeleteBuilder

from .models import Base, User


@pytest.fixture
def session() -> Session:
    return Base._session


@pytest.fixture
def builder(session: Session) -> DeleteBuilder:
    return DeleteBuilder(session, User())


def test_delete_builder_initial(builder: DeleteBuilder):
    assert isinstance(builder._model, User)
    assert builder.get_model_class() is User


def test_build_delete_stmt(builder: DeleteBuilder):
    builder._delete_stmt_initial()
    stmt = builder._delete_stmt

    assert isinstance(stmt, Delete)
    assert stmt.is_dml


def test_build_delete_stmt_with_single_where_clause(faker, builder: DeleteBuilder):
    builder.where(User.email == faker.email()).delete()

    stmt = builder._delete_stmt

    assert isinstance(stmt.whereclause, BinaryExpression)
    assert stmt.whereclause.left.name == "email"


def test_build_delete_stmt_with_multiple_where_clause(faker, builder: DeleteBuilder):
    builder.where(User.email == faker.email()).where(User.state.is_(False)).delete()
    stmt = builder._delete_stmt

    assert isinstance(stmt.whereclause, BooleanClauseList)

    validate_names = ["email", "state"]
    for idx, clause in enumerate(stmt.whereclause):
        assert isinstance(clause, BinaryExpression)
        assert clause.left.name == validate_names[idx]

    assert isinstance(stmt, Delete)
    assert stmt.is_dml


def test_build_delete_stmt_with_returning(builder: DeleteBuilder):
    builder.returning(User.id, User.email)

    stmt = builder._delete_stmt

    assert len(stmt._returning) > 0

    validate_names = ["id", "email"]
    for idx, col in enumerate(stmt._returning):
        assert isinstance(col, AnnotatedColumn)
        assert col.name == validate_names[idx]


def test_build_delete_stmt_with_returning_all(builder: DeleteBuilder):
    builder.returning(User)

    stmt = builder._delete_stmt

    assert len(stmt._returning) > 0

    for col in stmt._returning:
        assert isinstance(col, AnnotatedTable)


def test_call_delete(faker, builder: DeleteBuilder, session: Session):
    # seed
    user = User(name=faker.name(), email=faker.email(), password=faker.password())
    session.add(user)
    session.commit()

    builder.where(User.id == user.id).delete()

    #
    validate = session.execute(select(User).where(User.id == user.id)).scalars().first()
    assert validate is None


# def test_call_delete_with_soft_delete_scope(mocker, builder, session: Session):
#     mock_delete_stmt = mocker.patch.object(SoftDeleteScope, "_delete_stmt")
#     mock_execute = mocker.patch.object(DeleteBuilder, "execute")
#     mock_commit = mocker.patch.object(session, "commit")

#     builder.apply_scopes({SoftDeleteScope: SoftDeleteScope()})
#     builder.execute()

#     mock_delete_stmt.assert_called_once()
#     mock_execute.assert_called_once()
#     mock_commit.assert_called_once()
