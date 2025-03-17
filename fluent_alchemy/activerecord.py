import typing as t

from sqlalchemy import Insert, Select, Update, Delete
from sqlalchemy.orm import Session
from sqlalchemy.engine.result import Result

from .session import ScopedSessionHandler
from .builders.select import SelectBuilder
from .builders.insert import InsertBuilder
from .builders.update import UpdateBuilder
from .builders.delete import DeleteBuilder

T = t.TypeVar("T", bound="ActiveRecord")


class ActiveRecord(ScopedSessionHandler):
    @classmethod
    def select(cls: t.Type[T], *entities) -> SelectBuilder:
        return cls._new_select().select(*entities)

    @classmethod
    def first(cls: t.Type[T], session: t.Optional[Session] = None) -> t.Optional[T]:
        session = cls.get_session(session)

        return cls._new_select().execute(session=session).scalars().first()

    @classmethod
    def find(cls: t.Type[T], pk: t.Any, session: Session = None) -> t.Optional[T]:
        session = cls.get_session(session)

        return session.get(cls, pk)

    @classmethod
    def all(cls: t.Type[T], session: Session = None) -> t.Sequence[T]:
        session = cls.get_session(session)

        return cls._new_select().execute(session=session).scalars().all()

    @classmethod
    def create(cls: t.Type[T], attributes: dict, session: Session = None) -> T:
        session = cls.get_session(session)

        instance = cls(**attributes)
        instance.save(session)

        return instance

    @classmethod
    def where(cls: t.Type[T], *express) -> SelectBuilder:
        return cls._new_select().where(*express)

    @classmethod
    def order_by(cls: t.Type[T], *express) -> SelectBuilder:
        return cls._new_select().order_by(*express)

    @classmethod
    def offset(cls: t.Type[T], offset: int = 0) -> SelectBuilder:
        if not isinstance(offset, int):
            raise ValueError

        return cls._new_select().offset(offset)

    @classmethod
    def limit(cls: t.Type[T], limit: int = 0) -> SelectBuilder:
        if not isinstance(limit, int):
            raise ValueError

        return cls._new_select().limit(limit)

    @classmethod
    def insert(cls: t.Type[T], values) -> InsertBuilder:
        return InsertBuilder(cls, session=cls._session).values(values)

    @classmethod
    def update(cls: t.Type[T], **values) -> UpdateBuilder:
        return UpdateBuilder(cls, session=cls._session).values(**values)

    @classmethod
    def destroy(cls: t.Type[T]) -> DeleteBuilder:
        return DeleteBuilder(cls, session=cls._session)

    @classmethod
    def _new_select(cls: t.Type[T]) -> SelectBuilder:
        return SelectBuilder(cls, session=cls._session)

    @classmethod
    def execute(
        cls: t.Type[T],
        stmt: t.Union[Select, Insert, Update, Delete],
        session: t.Optional[Session] = None,
        *args,
        **kwargs,
    ) -> Result:
        session = cls.get_session(session)

        return session.execute(stmt, *args, **kwargs)

    # @classmethod
    # def paginate(cls, page: int = 1, per_page: int = 50, **kwargs):
    #     return cls()._new_select().paginate(page, per_page, **kwargs)

    def save(self, session: t.Optional[Session] = None, refresh: bool = True):
        session = self.get_session(session)

        try:
            session.add(self)
            session.commit()

            if refresh:
                session.refresh(self)

        except Exception as e:
            session.rollback()
            raise e

    def delete(self, session: t.Optional[Session] = None, commit: bool = True):
        session = self.get_session(session)

        try:
            session.delete(self)

            if commit:
                session.commit()

        except Exception as e:
            self._session.rollback()
            raise e
