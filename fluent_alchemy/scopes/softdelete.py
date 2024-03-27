from datetime import datetime

from . import Scope
from ..builder import QueryBuilder


class SoftDeleteScope(Scope):
    def __init__(self):
        self._builder: QueryBuilder = None

    def boot(self, builder: QueryBuilder):
        self._builder = builder
        self._builder._set_on_delete(self._on_delete)

    def apply(self, with_trashed: bool = False):
        if not with_trashed:
            self._builder.where(self._builder._get_model_class().deleted_at.is_(None))

    def _on_delete(self):
        model = self._builder._model

        # update the field "deleted_at" set datetime to now in model
        model.deleted_at = datetime.now()

        self._builder._session.add(model)
