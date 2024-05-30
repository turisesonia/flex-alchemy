from typing import Any

from sqlalchemy import delete
from sqlalchemy.engine.result import Result
from sqlalchemy.sql.dml import Delete


from .base import WhereBase


class DeleteBuilder(WhereBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._delete_stmt: Delete = None

    def _delete_stmt_initial(self):
        if self._delete_stmt is None:
            self._delete_stmt = delete(self.get_model_class())

    def returning(self, *entities):
        self._delete_stmt_initial()

        self._delete_stmt = self._delete_stmt.returning(*entities)

        return self

    def delete(self, autocommit: bool = False, *args, **kwargs) -> Result[Any]:
        self._delete_stmt_initial()

        if self._where_clauses:
            self._delete_stmt = self._delete_stmt.where(*self._where_clauses)

        result = self._session.execute(self._delete_stmt, *args, **kwargs)

        if autocommit:
            self._commit()

        return result
