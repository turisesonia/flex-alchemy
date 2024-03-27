from typing import Optional
from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker, scoped_session


class ScopedSessionHandler:
    _session: Optional[scoped_session] = None

    @classmethod
    def set_engine(cls, engine: Engine):
        if not isinstance(engine, Engine):
            raise ValueError("Only support Sqlalchemy Engine Object")

        cls._session = scoped_session(sessionmaker(engine))

    @classmethod
    def remove_scoped_session(cls):
        if cls._session:
            cls._session.remove()
