import math

from typing import Optional, Iterable

from sqlalchemy import select, func
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import BinaryExpression, UnaryExpression
from sqlalchemy.orm.strategy_options import Load

from . import _M
from .base import BaseBuilder


class SelectBuilder(BaseBuilder):
    def _initial(self):
        if self._stmt is None:
            self._stmt = select(self.get_model_class())

    def select(self, *entities):
        if self._stmt is not None:
            # TODO select statement is already initial
            raise Exception("")

        if not entities:
            self._stmt = select(self.get_model_class())
        else:
            self._stmt = select(*entities)

        return self

    def where(self, *express: BinaryExpression):
        self._initial()

        self._stmt = self._stmt.where(*express)

        return self

    def offset(self, offset: int):
        self._initial()

        self._stmt = self._stmt.offset(offset)

        return self

    def limit(self, limit: int):
        self._initial()

        self._stmt = self._stmt.limit(limit)

        return self

    def group_by(self, *entities):
        self._initial()

        self._stmt = self._stmt.group_by(*entities)

        return self

    def having(self, *express: BinaryExpression):
        self._initial()

        self._stmt = self._stmt.having(*express)

        return self

    def order_by(self, *express: UnaryExpression):
        self._initial()

        self._stmt = self._stmt.order_by(*express)

        return self

    def options(self, *options: Load):
        self._initial()

        self._stmt = self._stmt.options(*options)

        return self

    def first(
        self, stmt: Optional[Select] = None, partial_fields: bool = False
    ) -> Optional[_M]:
        stmt = stmt if stmt is not None else self._stmt

        result = self._execute(stmt)

        if partial_fields:
            return result.first()

        return result.scalars().first()

    def get(
        self, stmt: Optional[Select] = None, partial_fields: bool = False
    ) -> Iterable[_M]:
        stmt = stmt if stmt is not None else self._stmt

        result = self._execute(stmt)

        # todo handle joinload issue
        if partial_fields:
            return result.all()

        return result.scalars().all()

    def paginate(self, page: int = 1, per_page: int = 30) -> dict:
        self._offset = (page - 1) * per_page
        self._limit = per_page

        total_stmt = select(func.count()).select_from(self.get_model_class())
        if self._stmt.whereclause is not None:
            total_stmt = total_stmt.where(self._stmt.whereclause)

        total_rows = self.first(total_stmt)

        return {
            "total": total_rows,
            "per_page": per_page,
            "current_page": page,
            "last_page": math.ceil(total_rows / per_page),
            "data": self.get(),
        }
