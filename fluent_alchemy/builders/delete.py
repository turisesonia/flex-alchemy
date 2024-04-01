from typing import Optional

from sqlalchemy import delete
from sqlalchemy.sql.dml import Delete

from .base import BaseBuilder


class DeleteBuilder(BaseBuilder):
    def _delete_stmt(self, stmt: Optional[Delete] = None, **kwargs) -> Delete:
        if stmt is None:
            stmt = delete(self._get_model_class())

        # apply scopes query
        # for _, scope in self._scopes.items():
        #     scope.apply(**kwargs)

        if self._where_clauses:
            stmt = stmt.where(*self._where_clauses)

        if self._returnings:
            stmt = stmt.returning(*self._returnings)

        return stmt
