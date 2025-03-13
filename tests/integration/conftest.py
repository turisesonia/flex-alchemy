import os
import pytest

from dotenv import load_dotenv

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.engine import URL

from example.models.base import Base


@pytest.fixture(scope="session")
def engine() -> Engine:
    load_dotenv()

    DB_HOST = os.environ.get("DB_HOST")
    DB_PORT = os.environ.get("DB_PORT")
    DB_DATABASE = os.environ.get("DB_DATABASE")
    DB_USERNAME = os.environ.get("DB_USERNAME")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")

    connection_url = URL.create(
        drivername="postgresql+psycopg",
        host=DB_HOST,
        username=DB_USERNAME,
        password=DB_PASSWORD,
        database=DB_DATABASE,
        port=DB_PORT,
    )

    return create_engine(
        connection_url,
        echo=False,  # show sql execute log
        future=True,
        pool_size=20,
        pool_recycle=3600,  # pool close connection time
    )


@pytest.fixture(scope="session")
def session(engine: Engine) -> Session:
    return sessionmaker(engine, future=True)()


@pytest.fixture(autouse=True)
def bind_session(engine: Engine, session: Session):
    import sqlalchemy as sa

    Base.make_session(engine)

    with session as db:
        yield

        if engine.dialect.name == "postgresql":
            db.execute(sa.text("SET CONSTRAINTS ALL DEFERRED"))

        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())

        if engine.dialect.name == "postgresql":
            db.execute(sa.text("SET CONSTRAINTS ALL IMMEDIATE"))

        db.commit()

    Base.teardown_session()
