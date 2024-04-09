from typing import Any, Optional

from sqlalchemy import insert
from sqlalchemy.sql.dml import Insert
from sqlalchemy.engine.result import Result

from .base import BaseBuilder


class InsertBuilder(BaseBuilder):
    def _insert_stmt(self, stmt: Optional[Insert] = None, **kwargs) -> Insert:
        if stmt is None:
            stmt = insert(self.get_model_class())

        if self._returnings:
            stmt = stmt.returning(*self._returnings)

        if self._execution_options:
            stmt = stmt.execution_options(**self._execution_options)

        return stmt

    def insert(self, values: list[dict]) -> Result[Any]:
        stmt = self._insert_stmt()

        result = self.execute(stmt, values)

        self._session.commit()

        return result
