from typing import Any

from sqlalchemy import insert
from sqlalchemy.engine.result import Result

from .base import BaseBuilder


class InsertBuilder(BaseBuilder):
    def _initial(self):
        if self._stmt is None:
            self._stmt = insert(self.get_model_class())

    def returning(self, *entities):
        self._initial()

        self._stmt = self._stmt.returning(*entities)

        return self

    def execution_options(self, **options):
        self._initial()

        self._stmt = self._stmt.execution_options(**options)

        return self

    def values(self, *args, **kwargs):
        self._initial()

        self._stmt = self._stmt.values(*args, **kwargs)

        return self

    def execute(self, autocommit: bool = True, *args, **kwargs) -> Result[Any]:
        if self._stmt is None:
            # todo error message
            raise ValueError("")

        result = self._session.execute(self._stmt, *args, **kwargs)

        if autocommit:
            self._commit()

        return result
