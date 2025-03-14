import typing as t

from sqlalchemy.orm import Session

from .builders import _M
from .session import ScopedSessionHandler
from .builders.select import SelectBuilder
from .builders.insert import InsertBuilder
from .builders.update import UpdateBuilder
from .builders.delete import DeleteBuilder
from .builders.complex import WhereBuilder, ValuesBuilder

T = t.TypeVar("T", bound="ActiveRecord")


class ReturningParams(t.TypedDict):
    cols: t.Union[_M, t.Iterable]
    params: dict[str, t.Any]


class ActiveRecord(ScopedSessionHandler):
    __primary_key__: str = "id"

    @classmethod
    def select(cls: t.Type[T], *entities) -> SelectBuilder:
        return cls._new_select().select(*entities)

    @classmethod
    def first(cls: t.Type[T], session: Session = None) -> t.Optional[T]:
        return cls._new_select().execute(session=session).scalars().first()

    @classmethod
    def find(cls: t.Type[T], pk: t.Any, session: Session = None) -> t.Optional[T]:
        session = session or cls._session

        return session.get(cls, pk)

    @classmethod
    def all(cls: t.Type[T], session: Session = None) -> t.Sequence[T]:
        return cls._new_select().execute(session=session).scalars().all()

    @classmethod
    def create(cls: t.Type[T], attributes: dict, session: Session = None) -> T:
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
        return cls._new_insert().values(values)

    @classmethod
    def update(cls: t.Type[T], **values) -> UpdateBuilder:
        return cls._new_update().values(**values)

    @classmethod
    def _new_select(cls: t.Type[T]) -> SelectBuilder:
        return SelectBuilder(cls, session=cls._session)

    @classmethod
    def _new_insert(cls: t.Type[T]) -> InsertBuilder:
        return InsertBuilder(cls, session=cls._session)

    @classmethod
    def _new_update(cls: t.Type[T]) -> UpdateBuilder:
        return UpdateBuilder(cls, session=cls._session)

    @classmethod
    def _new_delete(cls: t.Type[T]) -> DeleteBuilder:
        return DeleteBuilder(cls, session=cls._session)

    # @classmethod
    # def paginate(cls, page: int = 1, per_page: int = 50, **kwargs):
    #     return cls()._new_select().paginate(page, per_page, **kwargs)

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
