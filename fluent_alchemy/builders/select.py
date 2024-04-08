import math
from typing import Optional, Iterable

from sqlalchemy import select, func
from sqlalchemy.sql import Select

from . import _M
from .base import BaseBuilder


class SelectBuilder(BaseBuilder):
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
