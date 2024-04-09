from typing import Any, Optional, Generic, Callable, Union

from sqlalchemy.orm import Session
from sqlalchemy.orm.strategy_options import Load
from sqlalchemy.engine.result import Result
from sqlalchemy.sql import Select
from sqlalchemy.sql.dml import Delete
from sqlalchemy.sql.elements import BinaryExpression, UnaryExpression

from . import _M


class BaseBuilder(Generic[_M]):
    _model: _M

    def __init__(self, session: Session, model: _M):
        self._session: Session = session
        self._model: _M = model
        self._select_entities = []
        self._where_clauses = []
        self._group_clauses = []
        self._having_clauses = []
        self._order_clauses = []
        self._offset: Optional[int] = None
        self._limit: Optional[int] = None
        self._options = []
        self._execution_options: Optional[dict] = None
        self._returnings = []
        self._scopes = {}
        self._macros = {}

    def select(self, *entities):
        self._select_entities.extend(entities)

        return self

    def where(self, *express: BinaryExpression):
        self._where_clauses.extend(express)

        return self

    def offset(self, offset: int):
        self._offset = offset

        return self

    def limit(self, limit: int):
        self._limit = limit

        return self

    def group_by(self, *entities):
        self._group_clauses.extend(entities)

        return self

    def having(self, *express: BinaryExpression):
        self._having_clauses.extend(express)

        return self

    def order_by(self, *express: UnaryExpression):
        self._order_clauses.extend(express)

        return self

    def returning(self, *entities):
        self._returnings.extend(entities)

        return self

    def options(self, *options: Load):
        self._options.extend(options)

        return self

    def execution_options(self, **options):
        if self._execution_options is None:
            self._execution_options = {}

        self._execution_options.update(options)

        return self

    def execute(self, stmt: Union[Select, Delete], *args, **kwargs) -> Result[Any]:
        return self._session.execute(stmt, *args, **kwargs)

    def get_model_class(self):
        return self._model.__class__

    def apply_scopes(self, scopes: dict = {}):
        self._scopes = scopes
        self._on_delete: Optional[Callable] = None

        for _, scope in self._scopes.items():
            scope.boot(self)

        return self

    def macro(self, name: str, callable_: Callable):
        if callable(callable_):
            self._macros[name] = callable_

        return self
