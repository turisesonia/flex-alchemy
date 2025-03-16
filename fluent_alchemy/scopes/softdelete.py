from datetime import datetime

from sqlalchemy import update
from . import Scope
from ..builders.select import SelectBuilder


class SoftDeleteScope(Scope):
    def __init__(self):
        self._builder: SelectBuilder = None

    def boot(self, builder: SelectBuilder):
        self._builder = builder

        self._builder.macro("_delete_stmt", self._delete_stmt)

    def apply(self, with_trashed: bool = False):
        if not with_trashed:
            self._builder.where(self._builder.get_model_class().deleted_at.is_(None))

    def _delete_stmt(self):
        stmt = update(self._builder.get_model_class())

        if self._builder._where_clauses:
            stmt = stmt.where(*self._builder._where_clauses)

        stmt = stmt.values(deleted_at=datetime.now())

        return stmt
