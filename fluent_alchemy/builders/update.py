from typing import Any

from sqlalchemy import Update, update
from sqlalchemy.engine.result import Result
from sqlalchemy.sql.elements import BinaryExpression

from .base import BaseBuilder


class UpdateBuilder(BaseBuilder):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._update_stmt: Update = update(self.get_model_class())

    def values(self, *args, **kwargs):
        self._update_stmt = self._update_stmt.values(*args, **kwargs)

        return self

    def where(self, *express: BinaryExpression):
        self._update_stmt = self._update_stmt.where(*express)

        return self

    def returning(self, *entities):
        self._update_stmt = self._update_stmt.returning(*entities)

        return self

    def execute(self, autocommit: bool = True, *args, **kwargs) -> Result[Any]:
        if self._update_stmt is None:
            # todo error message
            raise ValueError("")

        result = self._session.execute(self._update_stmt, *args, **kwargs)

        if autocommit:
            self._commit()

        return result
