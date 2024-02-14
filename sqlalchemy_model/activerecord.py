from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql import Selectable

from .session import SessionHandler


class ActiveRecord(SessionHandler):

    @classmethod
    def select(cls, *entities, **kw):
        return cls()._new_query().select(*entities, **kw)

    @classmethod
    def first(cls):
        return cls()._new_query().limit(1).first()

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
    def create(cls, **attributes):
        instance = cls(**attributes)

        instance.save()

        return instance

    def _new_query(self) -> "QueryBuilder":
        builder = QueryBuilder(self._db)

        builder.set_model(self.__class__)

        return builder

    def save(self, refresh: bool = True):
        try:
            self._db.add(self)
            self._db.commit()

            if refresh:
                self._db.refresh(self)

        except Exception as e:
            self._db.rollback()
            raise e

    def delete(self):
        try:
            self._db.delete(self)
            self._db.commit()

        except Exception as e:
            self._db.rollback()
            raise e

        return True


class QueryBuilder:
    def __init__(self, db: Session):
        self.db = db

        self.model = None
        self.stmt: Optional[Selectable] = None

    def set_model(self, model):
        self.model = model

    def select(self, *entities, **kw):
        if self.stmt:
            raise Exception("")

        self.stmt = select(*entities, *kw)

        return self

    def where(self, *express):
        if not isinstance(self.stmt, Selectable):
            self.select(self.model)

        self.stmt = self.stmt.where(*express)

        return self

    def limit(self, num: int):
        if not isinstance(self.stmt, Selectable):
            self.select(self.model)

        self.stmt = self.stmt.limit(num)

        return self

    def first(self):
        return self.db.scalar(self.stmt)

    def get(self):
        if not isinstance(self.stmt, Selectable):
            self.select(self.model)

        return self.db.scalars(self.stmt).all()
