import math

from typing import Any, Optional, Iterable

from sqlalchemy import select, func, Executable
from sqlalchemy.sql.elements import BinaryExpression, UnaryExpression
from sqlalchemy.engine.result import Result
from sqlalchemy.orm.strategy_options import Load
from sqlalchemy.sql import Select

from . import _M
from .base import BaseBuilder, WhereBase


class SelectBuilder(BaseBuilder, WhereBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._select_stmt: Select = None

    def _initial(self):
        if self._select_stmt is None:
            self._select_stmt = select(self.get_model_class())

    def select(self, *entities):
        if self._select_stmt is not None:
            # TODO select statement is already initial
            raise Exception("")

        if not entities:
            self._select_stmt = select(self.get_model_class())
        else:
            self._select_stmt = select(*entities)

        return self

    def offset(self, offset: int):
        self._initial()

        self._select_stmt = self._select_stmt.offset(offset)

        return self

    def limit(self, limit: int):
        self._initial()

        self._select_stmt = self._select_stmt.limit(limit)

        return self

    def group_by(self, *entities):
        self._initial()

        self._select_stmt = self._select_stmt.group_by(*entities)

        return self

    def having(self, *express: BinaryExpression):
        self._initial()

        self._select_stmt = self._select_stmt.having(*express)

        return self

    def order_by(self, *express: UnaryExpression):
        self._initial()

        self._select_stmt = self._select_stmt.order_by(*express)

        return self

    def options(self, *options: Load):
        self._initial()

        self._select_stmt = self._select_stmt.options(*options)

        return self

    def execute(
        self, stmt: Optional[Executable] = None, *args, **kwargs
    ) -> Result[Any]:
        stmt = stmt if stmt is not None else self._select_stmt

        return self._session.execute(stmt, *args, **kwargs)

    def first(self, specific_fields: bool = False) -> Optional[_M]:
        if self._where_clauses:
            self._select_stmt.where(*self._where_clauses)

        result = self.execute(self._select_stmt)

        if specific_fields:
            return result.first()

        return result.scalars().first()

    def get(self, specific_fields: bool = False) -> Iterable[_M]:
        if self._where_clauses:
            self._select_stmt.where(*self._where_clauses)

        result = self.execute(self._select_stmt)

        if specific_fields:
            return result.all()

        return result.scalars().all()

    def paginate(self, page: int = 1, per_page: int = 30) -> dict:
        self.offset((page - 1) * per_page)
        self.limit(per_page)

        if self._where_clauses:
            self._select_stmt.where(*self._where_clauses)

        total_stmt = select(func.count()).select_from(self.get_model_class())
        if self._select_stmt.whereclause is not None:
            total_stmt = total_stmt.where(self._select_stmt.whereclause)

        total_rows = self.execute(total_stmt).scalars().first()

        return {
            "total": total_rows,
            "per_page": per_page,
            "current_page": page,
            "last_page": math.ceil(total_rows / per_page),
            "data": self.get(),
        }
