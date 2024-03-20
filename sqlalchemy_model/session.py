from typing import Optional
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker, scoped_session


class SessionHandler:
    _session: Optional[Session] = None

    @classmethod
    def set_engine(cls, engine: Engine):
        if not isinstance(engine, Engine):
            raise ValueError("Only support Sqlalchemy Engine Object")

        cls._session = scoped_session(sessionmaker(engine))

    @classmethod
    def remove_scoped_session(cls):
        if cls._session:
            cls._session.remove()

    @classmethod
    def close_session(cls):
        if cls._session:
            cls._session.close()
