from typing import Optional, Generic, Callable

from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import BinaryExpression

from . import _M


class BaseBuilder(Generic[_M]):
    def __init__(self, session: Session, model: _M):
        self._session: Session = session
        self._model: _M = model

        self._scopes = {}
        self._macros = {}

    def _commit(self):
        self._session.commit()

    def get_model_class(self):
        return self._model.__class__

    def boot_scopes(self, scopes: dict = {}):
        self._scopes = scopes
        self._on_delete: Optional[Callable] = None

        for _, scope in self._scopes.items():
            scope.boot(self)

        return self

    def macro(self, name: str, callable_: Callable):
        if callable(callable_):
            self._macros[name] = callable_

        return self


class WhereBase(BaseBuilder):
    _where_clauses = ()

    def where(self, *express: BinaryExpression):
        self._where_clauses += (*express,)

        return self


class ValueBase(BaseBuilder):
    _values = None

    _returning = ()

    def values(self, *args, **kwargs):
        if args:
            self._values = args[0]
        else:
            self._values = kwargs

        return self

    def returning(self, *entities):
        self._returning += (*entities,)

        return self
