from . import Scope
from ..builder import QueryBuilder


class SoftDeleteScope(Scope):
    def __init__(self):
        self._builder: QueryBuilder = None

    def boot(self, builder: QueryBuilder):
        self._builder = builder
        self._builder._set_macros("with_trashed", self._with_trashed)

    def apply(self):
        return self._builder.where(self._builder._model.deleted_at.is_(None))

    def _with_trashed(self):
        self._builder._remove_scope(self.__class__)

        return self._builder
