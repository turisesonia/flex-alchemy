from typing import Any

from sqlalchemy import Insert, insert
from sqlalchemy.engine.result import Result

from .base import ValueBase


class InsertBuilder(ValueBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._insert_stmt: Insert = insert(self.get_model_class())

    def execution_options(self, **options):
        self._insert_stmt = self._insert_stmt.execution_options(**options)

        return self

    def insert(self, autocommit: bool = True, *args, **kwargs) -> Result[Any]:
        if not self._values:
            raise ValueError("Values cannot be empty.")

        self._insert_stmt = self._insert_stmt.values(self._values)

        if self._returning:
            self._insert_stmt = self._insert_stmt.returning(*self._returning)

        result = self._session.execute(self._insert_stmt, *args, **kwargs)

        if autocommit:
            self._commit()

        return result
