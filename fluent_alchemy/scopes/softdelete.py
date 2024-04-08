from datetime import datetime

from sqlalchemy import update
from . import Scope
from ..builders.query import QueryBuilder


class SoftDeleteScope(Scope):
    def __init__(self):
        self._builder: QueryBuilder = None

    def boot(self, builder: QueryBuilder):
        self._builder = builder

        self._builder.macro("_delete_stmt", self._delete_stmt)

    def apply(self, with_trashed: bool = False):
        if not with_trashed:
            self._builder.where(self._builder._get_model_class().deleted_at.is_(None))

    def _delete_stmt(self):
        stmt = update(self._builder._get_model_class())

        if self._builder._where_clauses:
            stmt = stmt.where(*self._builder._where_clauses)

        stmt = stmt.values(deleted_at=datetime.now())

        return stmt
