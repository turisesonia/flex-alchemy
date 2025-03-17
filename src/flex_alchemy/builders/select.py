from typing import Optional

from sqlalchemy import Executable
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import BinaryExpression, UnaryExpression
from sqlalchemy.engine.result import Result
from sqlalchemy.orm.strategy_options import Load
from sqlalchemy.sql import Select

from .base import BaseWhereBuilder


class SelectBuilder(BaseWhereBuilder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._entities: tuple = ()
        self._offset: int | None = None
        self._limit: int | None = None
        self._group_by: tuple = ()
        self._having: tuple = ()
        self._order_by: tuple = ()
        self._options: tuple = ()

    def select(self, *entities):
        self._entities += (*entities,)

        return self

    def offset(self, offset: int):
        self._offset = offset

        return self

    def limit(self, limit: int):
        self._limit = limit

        return self

    def group_by(self, *entities):
        self._group_by += (*entities,)

        return self

    def having(self, *express: BinaryExpression):
        self._having += (*express,)

        return self

    def order_by(self, *express: UnaryExpression):
        self._order_by += (*express,)

        return self

    def options(self, *options: Load):
        self._options += (*options,)

        return self

    def _build(self) -> Select:
        if self._entities:
            stmt = Select(*self._entities)
        else:
            stmt = Select(self._model)

        if self._where_clauses:
            stmt = stmt.where(*self._where_clauses)

        if self._offset is not None:
            stmt = stmt.offset(self._offset)

        if self._limit is not None:
            stmt = stmt.limit(self._limit)

        if self._group_by:
            stmt = stmt.group_by(*self._group_by)

        if self._having:
            stmt = stmt.having(*self._having)

        if self._order_by:
            stmt = stmt.order_by(*self._order_by)

        if self._options:
            stmt = stmt.options(*self._options)

        return stmt

    def execute(
        self, session: Optional[Session] = None, *args, **kwargs
    ) -> Result:
        session = self.get_session(session)

        stmt = self._build()

        return session.execute(stmt, *args, **kwargs)

    # def paginate(self, page: int = 1, per_page: int = 30) -> dict:
    #     self.offset((page - 1) * per_page)
    #     self.limit(per_page)

    #     if self._where_clauses:
    #         self._stmt = self._stmt.where(*self._where_clauses)

    #     total_stmt = select(func.count()).select_from(self.get_model_class())
    #     if self._stmt.whereclause is not None:
    #         total_stmt = total_stmt.where(self._stmt.whereclause)

    #     total_rows = self.execute(total_stmt).scalars().first()

    #     return {
    #         "total": total_rows,
    #         "per_page": per_page,
    #         "current_page": page,
    #         "last_page": math.ceil(total_rows / per_page),
    #         "data": self.get(),
    #     }
