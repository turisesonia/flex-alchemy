from typing import Optional

from sqlalchemy import delete
from sqlalchemy.sql.dml import Delete

from .base import BaseBuilder


class DeleteBuilder(BaseBuilder):
    def _delete_stmt(self, stmt: Optional[Delete] = None, **kwargs) -> Delete:
        if stmt is None:
            stmt = delete(self.get_model_class())

        if self._where_clauses:
            stmt = stmt.where(*self._where_clauses)

        if self._returnings:
            stmt = stmt.returning(*self._returnings)

        return stmt

    def delete(self, force: bool = False):
        if not force and (macro_method := self._macros.get("_delete_stmt")):
            stmt = macro_method()
        else:
            stmt = self._delete_stmt()

        result = self.execute(stmt)
        self._session.commit()

        return result
