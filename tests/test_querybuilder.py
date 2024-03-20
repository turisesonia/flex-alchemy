import pytest

from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy_model.builder import QueryBuilder

from .models import User


@pytest.fixture
def session(engine) -> Session:
    session = sessionmaker(engine)
    return session()


def test_with_scope_boot(mocker, session: Session):
    mock_scope = mocker.Mock()

    QueryBuilder(session, User, {mock_scope.__class__: mock_scope})

    mock_scope.boot.assert_called_once()
