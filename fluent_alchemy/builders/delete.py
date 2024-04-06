from typing import Optional
from datetime import datetime

from sqlalchemy import delete, update
from sqlalchemy.sql.dml import Delete, Update

from .base import BaseBuilder


class DeleteBuilder(BaseBuilder):
    def _delete_stmt(self, stmt: Optional[Delete] = None, **kwargs) -> Delete:
        if stmt is None:
            stmt = delete(self._get_model_class())

        if self._where_clauses:
            stmt = stmt.where(*self._where_clauses)

        if self._returnings:
            stmt = stmt.returning(*self._returnings)

        return stmt

    def _soft_delete_stmt(self) -> Update:
        stmt = update(self._get_model_class())

        if self._where_clauses:
            stmt = stmt.where(*self._where_clauses)

        stmt.values(deleted_at=datetime.now())

        return stmt

    def delete(self, force: bool = False):
        stmt = self._delete_stmt()

        result = self.execute(stmt)

        self._session.commit()

        return result
