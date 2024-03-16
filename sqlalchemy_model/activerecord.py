import math

from typing import Optional
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.orm import scoped_session
from sqlalchemy.sql import Select

from .session import SessionHandler
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


class QueryBuilder:
    def __init__(self, session: scoped_session, model):
        self._session = session
        self._model = model
        self._select_entities = []
        self._where_clauses = []
        self._order_clauses = []
        self._offset: Optional[int] = None
        self._limit: Optional[int] = None
        self._options = []

        # soft deleted
        self._with_trashed: bool = False

    def select(self, *entities):
        self._select_entities.extend(entities)

        return self

    def where(self, *express):
        self._where_clauses.extend(express)

        return self

    def offset(self, offset: int):
        self._offset = offset

        return self

    def limit(self, limit: int):
        self._limit = limit

        return self

    def paginate(self, page: int = 1, per_page: int = 50):
        self._offset = (page - 1) * per_page
        self._limit = per_page

        total_rows = self.first(
            self._get_stmt(
                select(func.count()).select_from(self._model),
                pageable=True,
            )
        )

        return {
            "total": total_rows,
            "per_page": per_page,
            "current_page": page,
            "last_page": math.ceil(total_rows / per_page),
            "data": self.get(),
        }

    def order_by(self, *express):
        self._order_clauses.extend(express)

        return self

    def options(self, *options):
        self._options.extend(options)

        return self

    def with_trashed(self):
        self._with_trashed = True

        return self

    def first(self, stmt: Optional[Select] = None):
        stmt = stmt if stmt is not None else self._get_stmt()

        return self._session.scalar(stmt)

    def get(self, stmt: Optional[Select] = None):
        stmt = stmt if stmt is not None else self._get_stmt()

        return self._session.scalars(stmt).all()

    def _is_softdeleted(self) -> bool:
        return hasattr(self._model, "deleted_at")

    def _get_stmt(
        self, stmt: Optional[Select] = None, pageable: bool = False
    ) -> Select:
        if stmt is None:
            if self._select_entities:
                stmt = select(*self._select_entities)
            else:
                stmt = select(self._model)

        if self._is_softdeleted() and not self._with_trashed:
            stmt = stmt.where(self._model.deleted_at.is_(None))

        if self._where_clauses:
            stmt = stmt.where(*self._where_clauses)

        if not pageable and self._order_clauses:
            stmt = stmt.order_by(*self._order_clauses)

        if not pageable and self._offset is not None:
            stmt = stmt.offset(self._offset)

        if not pageable and self._limit is not None:
            stmt = stmt.limit(self._limit)

        if self._options:
            stmt = stmt.options(*self._options)

        return stmt
