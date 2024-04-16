from typing import Any

from sqlalchemy import update
from sqlalchemy.engine.result import Result
from sqlalchemy.sql.elements import BinaryExpression

from .base import BaseBuilder


class UpdateBuilder(BaseBuilder):
    def _initial(self):
        if self._stmt is None:
            self._stmt = update(self.get_model_class())

    def where(self, *express: BinaryExpression):
        self._initial()

        self._stmt = self._stmt.where(*express)

        return self

    def returning(self, *entities):
        self._initial()

        self._stmt = self._stmt.returning(*entities)

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
