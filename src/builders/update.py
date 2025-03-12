from typing import Any

from sqlalchemy import Update, update
from sqlalchemy.engine.result import Result
from sqlalchemy.sql.elements import BinaryExpression

from .base import ValueBase


class UpdateBuilder(ValueBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._update_stmt: Update = update(self.get_model_class())

    def where(self, *express: BinaryExpression):
        self._update_stmt = self._update_stmt.where(*express)

        return self

    def update(self, autocommit: bool = True, *args, **kwargs) -> Result[Any]:
        if not self._values:
            raise ValueError("Values cannot be empty.")

        self._update_stmt = self._update_stmt.values(self._values)

        if self._returning:
            self._update_stmt = self._update_stmt.returning(*self._returning)

        result = self._session.execute(self._update_stmt, *args, **kwargs)

        if autocommit:
            self._commit()

        return result
