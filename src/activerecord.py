import typing as t

from sqlalchemy.orm import Session

from .builders import _M
from .session import ScopedSessionHandler
from .builders.select import SelectBuilder
from .builders.delete import DeleteBuilder
from .builders.insert import InsertBuilder
from .builders.complex import WhereBuilder, ValuesBuilder


class ReturningParams(t.TypedDict):
    cols: t.Union[_M, t.Iterable]
    params: dict[str, t.Any]


class ActiveRecord(ScopedSessionHandler):
    __primary_key__: str = "id"

    @classmethod
    def select(cls, *entities):
        return cls._new_select().select(*entities)

    @classmethod
    def first(cls, session: Session = None) -> t.Optional[_M]:
        return cls._new_select(session).execute().scalars().first()

    @classmethod
    def find(cls, pk: t.Any, session: Session = None):
        session = session or cls._session

        return session.get(cls, pk)

    @classmethod
    def all(cls, session: Session = None) -> t.Iterable:
        return cls._new_select(session).execute().scalars().all()

    @classmethod
    def where(cls, *express, session: Session = None):
        return cls._new_select(session).where(*express)

    @classmethod
    def order_by(cls, *express, session: Session = None):
        return cls._new_select(session).order_by(*express)

    @classmethod
    def offset(cls, offset: int = 0, session: Session = None):
        if not isinstance(offset, int):
            raise ValueError

        return cls._new_select(session).offset(offset)

    @classmethod
    def limit(cls, limit: int = 0, session: Session = None):
        if not isinstance(limit, int):
            raise ValueError

        return cls._new_select(session).limit(limit)

    # @classmethod
    # def paginate(cls, page: int = 1, per_page: int = 50, **kwargs):
    #     return cls()._new_select().paginate(page, per_page, **kwargs)

    @classmethod
    def create(cls, attributes: dict, session: Session = None):
        instance = cls(**attributes)

        instance.save(session)

        return instance

    @classmethod
    def insert(
        cls,
        values,
        session: Session = None,
        returning: bool = False,
        execution_options: dict = None,
        commit: bool = True,
        **kwargs,
    ):
        builder = InsertBuilder(session or cls._session, cls)

        builder.values(values)

        if execution_options is not None:
            builder.execution_options(execution_options)

        if returning:
            # TODO add accept extra params feature
            builder.returning(cls)

        return builder.execute(session=session, commit=commit, **kwargs)

    @classmethod
    def values(cls, *args, **kwargs):
        return cls()._new_values().values(*args, **kwargs)

    @classmethod
    def _new_select(cls, session: Session = None) -> SelectBuilder:
        return SelectBuilder(session or cls._session, cls)

    @classmethod
    def _new_delete(cls) -> DeleteBuilder:
        return DeleteBuilder(cls._session, cls)

    @classmethod
    def _new_where(cls) -> WhereBuilder:
        return WhereBuilder(cls._session, cls)

    @classmethod
    def _new_values(cls) -> ValuesBuilder:
        return ValuesBuilder(cls._session, cls)

    def save(self, session: Session = None, refresh: bool = True):
        session = session or self._session
        try:
            session.add(self)
            session.commit()

            if refresh:
                session.refresh(self)

        except Exception as e:
            session.rollback()
            raise e

    def delete(self, autocommit: bool = True, *args, **kwargs):
        try:
            model_primary_key = getattr(self.__class__, self.__primary_key__)
            model_value = getattr(self, self.__primary_key__)

            self._new_delete().where(model_primary_key == model_value).delete(
                autocommit=autocommit, *args, **kwargs
            )

        except Exception as e:
            self._session.rollback()
            raise e
