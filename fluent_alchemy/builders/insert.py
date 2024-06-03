from typing import Any

from sqlalchemy import Insert, insert
from sqlalchemy.engine.result import Result

from .base import BaseBuilder, Returning


class InsertBuilder(BaseBuilder, Returning):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._insert_stmt: Insert = insert(self.get_model_class())

    def values(self, *args, **kwargs):
        self._insert_stmt = self._insert_stmt.values(*args, **kwargs)

        return self

    def execution_options(self, **options):
        self._insert_stmt = self._insert_stmt.execution_options(**options)

        return self

    def insert(self, autocommit: bool = True, *args, **kwargs) -> Result[Any]:
        if self._returning:
            self._insert_stmt = self._insert_stmt.returning(*self._returning)

        result = self._session.execute(self._insert_stmt, *args, **kwargs)

        if autocommit:
            self._commit()

        return result
