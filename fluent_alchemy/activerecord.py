from typing import Sequence

from .session import ScopedSessionHandler
from .builder import QueryBuilder


class ActiveRecord(ScopedSessionHandler):
    @classmethod
    def select(cls, *entities):
        return cls()._new_query().select(*entities)

    @classmethod
    def first(cls, **kwargs):
        return cls()._new_query().first(**kwargs)

    @classmethod
    def find(cls, id_: int, **kwargs):
        return cls()._new_query().where(cls.id == id_).first(**kwargs)

    @classmethod
    def all(cls, **kwargs) -> Sequence:
        return cls()._new_query().get(**kwargs)

    @classmethod
    def where(cls, *express):
        return cls()._new_query().where(*express)

    @classmethod
    def order_by(cls, *express):
        return cls()._new_query().order_by(*express)

    @classmethod
    def offset(cls, offset: int = 0):
        if not isinstance(offset, int):
            raise ValueError

        return cls()._new_query().offset(offset)

    @classmethod
    def limit(cls, limit: int = 0):
        if not isinstance(limit, int):
            raise ValueError

        return cls()._new_query().limit(limit)

    @classmethod
    def paginate(cls, page: int = 1, per_page: int = 50, **kwargs):
        return cls()._new_query().paginate(page, per_page, **kwargs)

    @classmethod
    def create(cls, **attributes):
        instance = cls(**attributes)

        instance.save()

        return instance

    def _new_query(self) -> "QueryBuilder":
        scopes = {}

        for base in self.__class__.__bases__:
            if hasattr(base, "scope_registry"):
                scope = base.scope_registry()
                scopes[scope.__class__] = scope

        return QueryBuilder(self._session, self, scopes)

    def save(self, refresh: bool = True):
        try:
            self._session.add(self)
            self._session.commit()

            if refresh:
                self._session.refresh(self)

        except Exception as e:
            self._session.rollback()
            raise e

    def delete(self, force: bool = False):
        try:
            self._new_query().delete(force)

        except Exception as e:
            self._session.rollback()
            raise e
