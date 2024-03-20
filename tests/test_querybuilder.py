from sqlalchemy.orm import Session

from sqlalchemy_model.builder import QueryBuilder
from sqlalchemy_model.scopes.softdelete import SoftDeleteScope
from .models import User


def test_with_scope_boot(mocker, session: Session):
    mock_scope = mocker.Mock()

    QueryBuilder(session, User, {mock_scope.__class__: mock_scope})

    mock_scope.boot.assert_called_once()


def test_soft_delete_scope(mocker, session: Session):
    scopes = {SoftDeleteScope.__class__: SoftDeleteScope()}

    builder = QueryBuilder(session, User(), scopes)

    assert callable(builder._on_delete)
