from typing import Optional, Any

from sqlalchemy import delete
from sqlalchemy.sql.dml import Delete
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.engine.result import Result


from .base import BaseBuilder


class DeleteBuilder(BaseBuilder):
    def _initial(self):
        if self._stmt is None:
            self._stmt = delete(self.get_model_class())

    def where(self, *express: BinaryExpression):
        self._initial()

        self._stmt = self._stmt.where(*express)

        return self

    def returning(self, *entities):
        self._initial()

        self._stmt = self._stmt.returning(*entities)

        return self

    def execute(self, autocommit: bool = True, *args, **kwargs) -> Result[Any]:
        self._initial()

        result = self._session.execute(self._stmt, *args, **kwargs)

        if autocommit:
            self._commit()

        return result
