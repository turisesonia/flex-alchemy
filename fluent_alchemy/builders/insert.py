from typing import Any

from sqlalchemy import Insert, insert
from sqlalchemy.engine.result import Result

from .base import BaseBuilder


class InsertBuilder(BaseBuilder):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._insert_stmt: Insert = None

    def _initial(self):
        if self._insert_stmt is None:
            self._insert_stmt = insert(self.get_model_class())

    def returning(self, *entities):
        self._initial()

        self._insert_stmt = self._insert_stmt.returning(*entities)

        return self

    def execution_options(self, **options):
        self._initial()

        self._insert_stmt = self._insert_stmt.execution_options(**options)

        return self

    def values(self, *args, **kwargs):
        self._initial()

        self._insert_stmt = self._insert_stmt.values(*args, **kwargs)

        return self

    def execute(self, autocommit: bool = True, *args, **kwargs) -> Result[Any]:
        if self._insert_stmt is None:
            # todo error message
            raise ValueError("")

        result = self._session.execute(self._insert_stmt, *args, **kwargs)

        if autocommit:
            self._commit()

        return result
