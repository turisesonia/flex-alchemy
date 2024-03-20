from datetime import datetime

from . import Scope
from ..builder import QueryBuilder


class SoftDeleteScope(Scope):
    def __init__(self):
        self._builder: QueryBuilder = None

    def boot(self, builder: QueryBuilder):
        self._builder = builder
        self._builder._set_macros("with_trashed", self._with_trashed)
        self._builder._set_on_delete(self._on_delete)

    def apply(self):
        self._builder.where(self._builder._get_model_class().deleted_at.is_(None))

    def _with_trashed(self):
        self._builder._remove_scope(self.__class__)

        return self._builder

    def _on_delete(self):
        model = self._builder._model

        model.deleted_at = datetime.now()

        self._builder._session.add(model)
