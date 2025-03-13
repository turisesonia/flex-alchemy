from typing import Any

from sqlalchemy import delete
from sqlalchemy.engine.result import Result
from sqlalchemy.sql.dml import Delete


from .base import WhereBase


class DeleteBuilder(WhereBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._delete_stmt: Delete = delete(self.get_model_class())

    def returning(self, *entities):
        self._delete_stmt = self._delete_stmt.returning(*entities)

        return self

    def delete(self, autocommit: bool = True, *args, **kwargs) -> Result[Any]:
        if self._where_clauses:
            self._delete_stmt = self._delete_stmt.where(*self._where_clauses)

        result = self._session.execute(self._delete_stmt, *args, **kwargs)

        if autocommit:
            self._commit()

        return result
