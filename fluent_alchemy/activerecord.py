from typing import Sequence

from .session import ScopedSessionHandler
from .builders.select import SelectBuilder
from .builders.insert import InsertBuilder
from .builders.update import UpdateBuilder
from .builders.delete import DeleteBuilder
from .builders.where import WhereBuilder


class ActiveRecord(ScopedSessionHandler):
    @classmethod
    def select(cls, *entities):
        return cls()._new_select().select(*entities)

    @classmethod
    def first(cls, **kwargs):
        return cls()._new_select().first(**kwargs)

    @classmethod
    def find(cls, id_: int, **kwargs):
        return cls()._new_select().where(cls.id == id_).first(**kwargs)

    @classmethod
    def all(cls, **kwargs) -> Sequence:
        return cls()._new_select().select().get(**kwargs)

    @classmethod
    def where(cls, *express):
        return cls()._new_where().where(*express)

    @classmethod
    def order_by(cls, *express):
        return cls()._new_select().order_by(*express)

    @classmethod
    def offset(cls, offset: int = 0):
        if not isinstance(offset, int):
            raise ValueError

        return cls()._new_select().offset(offset)

    @classmethod
    def limit(cls, limit: int = 0):
        if not isinstance(limit, int):
            raise ValueError

        return cls()._new_select().limit(limit)

    @classmethod
    def paginate(cls, page: int = 1, per_page: int = 50, **kwargs):
        return cls()._new_select().paginate(page, per_page, **kwargs)

    @classmethod
    def create(cls, **attributes):
        instance = cls(**attributes)

        instance.save()

        return instance

    @classmethod
    def insert(cls) -> InsertBuilder:
        return cls()._new_insert()

    @classmethod
    def update(cls):
        return cls()._new_update()

    def _new_select(self) -> SelectBuilder:
        return SelectBuilder(self._session, self)

    def _new_insert(self) -> InsertBuilder:
        return InsertBuilder(self._session, self)

    def _new_update(self) -> UpdateBuilder:
        return UpdateBuilder(self._session, self)

    def _new_delete(self) -> DeleteBuilder:
        return DeleteBuilder(self._session, self)

    def _new_where(self) -> WhereBuilder:
        return WhereBuilder(self._session, self)

    def save(self, refresh: bool = True):
        try:
            self._session.add(self)
            self._session.commit()

            if refresh:
                self._session.refresh(self)

        except Exception as e:
            self._session.rollback()
            raise e

    def delete(self, autocommit: bool = False, *args, **kwargs):
        try:
            self._new_delete().where(self.__class__.id == self.id).delete(
                autocommit=autocommit, *args, **kwargs
            )

        except Exception as e:
            self._session.rollback()
            raise e
