from datetime import datetime

from .session import SessionHandler
from .builder import QueryBuilder
from .mixins.timestamp import TimestampMixin


class ActiveRecord(SessionHandler, TimestampMixin):
    @classmethod
    def select(cls, *entities):
        return cls()._new_query().select(*entities)

    @classmethod
    def first(cls):
        return cls()._new_query().first()

    @classmethod
    def find(cls, id_: int):
        return cls()._new_query().where(cls.id == id_).first()

    @classmethod
    def all(cls):
        return cls()._new_query().get()

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
        builder = QueryBuilder(self._session, self.__class__)

        return builder

    def _is_softdeleted(self) -> bool:
        return hasattr(self, "deleted_at")

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
            if self._is_softdeleted and not force:
                self._softdelete()
            else:
                self._session.delete(self)
                self._session.commit()

        except Exception as e:
            self._session.rollback()
            raise e

        return True

    def _softdelete(self):
        try:
            self.deleted_at = datetime.now()
            self.save()

        except Exception as e:
            self._session.rollback()
            raise e

        return True
