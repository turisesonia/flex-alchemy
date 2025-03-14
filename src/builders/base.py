import typing as t

from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import BinaryExpression


_M = t.TypeVar("_M")


class BaseBuilder(t.Generic[_M]):
    def __init__(self, model: _M, session: t.Optional[Session] = None):
        self._model: _M = model
        self._session: Session = session

        self._scopes = {}
        self._macros = {}

    def _commit(self):
        if isinstance(self._session, Session):
            self._session.commit()

    def boot_scopes(self, scopes: dict = {}):
        self._scopes = scopes
        self._on_delete: t.Optional[t.Callable] = None

        for _, scope in self._scopes.items():
            scope.boot(self)

        return self

    def macro(self, name: str, callable_: t.Callable):
        if callable(callable_):
            self._macros[name] = callable_

        return self


class BaseWhereBuilder(BaseBuilder):
    _where_clauses = ()

    def where(self, *express: BinaryExpression):
        self._where_clauses += (*express,)

        return self


class BaseValueBuilder(BaseBuilder):
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
