import math

from typing import Any, Optional, Generic, Iterable, TypeVar, Callable

from sqlalchemy import inspect, select, delete, func
from sqlalchemy.orm import Session
from sqlalchemy.orm.strategy_options import Load
from sqlalchemy.engine.result import Result
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import BinaryExpression, UnaryExpression

_M = TypeVar("_M")


class QueryBuilder(Generic[_M]):
    _model: _M

    def __init__(self, session: Session, model: _M, scopes: dict = {}):
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

        self._macros = {}
        self._scopes = scopes
        self._on_delete: Optional[Callable] = None

        self._boot_scopes()

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

    def options(self, *options: Load):
        self._options.extend(options)

        return self

    def execute(self, stmt: Select) -> Result[Any]:
        return self._session.execute(stmt)

    def first(self, stmt: Optional[Select] = None, **kwargs) -> Optional[_M]:
        stmt = stmt if stmt is not None else self._select_stmt(**kwargs)

        if len(self._select_entities) > 1:
            return self.execute(stmt).first()

        return self.execute(stmt).scalars().first()

    def get(self, stmt: Optional[Select] = None, **kwargs) -> Iterable[_M]:
        stmt = stmt if stmt is not None else self._select_stmt(**kwargs)

        if len(self._select_entities) > 1:
            return self.execute(stmt).all()

        return self.execute(stmt).scalars().all()

    def paginate(self, page: int = 1, per_page: int = 50) -> dict:
        self._offset = (page - 1) * per_page
        self._limit = per_page

        total_rows = self.first(
            self._select_stmt(
                select(func.count()).select_from(self._get_model_class()),
                pageable=True,
            )
        )

        return {
            "total": total_rows,
            "per_page": per_page,
            "current_page": page,
            "last_page": math.ceil(total_rows / per_page),
            "data": self.get(),
        }

    def _boot_scopes(self):
        for _, scope in self._scopes.items():
            scope.boot(self)

    def _get_model_class(self):
        return self._model.__class__

    def _select_stmt(
        self, stmt: Optional[Select] = None, pageable: bool = False, **kwargs
    ) -> Select:
        if stmt is None:
            stmt = (
                select(*self._select_entities)
                if self._select_entities
                else select(self._get_model_class())
            )

        # apply scopes query
        for _, scope in self._scopes.items():
            scope.apply(**kwargs)

        if self._where_clauses:
            stmt = stmt.where(*self._where_clauses)

        if not pageable and self._group_clauses:
            stmt = stmt.group_by(*self._group_clauses)

        if not pageable and self._group_clauses and self._having_clauses:
            stmt = stmt.group_by(*self._having_clauses)

        if not pageable and self._order_clauses:
            stmt = stmt.order_by(*self._order_clauses)

        if not pageable and self._offset is not None:
            stmt = stmt.offset(self._offset)

        if not pageable and self._limit is not None:
            stmt = stmt.limit(self._limit)

        if self._options:
            stmt = stmt.options(*self._options)

        return stmt

    # * Delete query builder
    def delete(self, force: bool = False):
        if self._on_delete and not force:
            self._on_delete()
        else:
            self._do_delete()

        self._session.commit()

    def _set_on_delete(self, callback: Callable):
        self._on_delete = callback

    def _do_delete(self):
        if inspect(self._model).persistent:
            self._session.delete(self._model)
        else:
            self._session.execute(self._delete_stmt())

    def _delete_stmt(self):
        stmt = delete(self._get_model_class())

        if self._where_clauses:
            stmt = stmt.where(*self._where_clauses)

        return stmt
