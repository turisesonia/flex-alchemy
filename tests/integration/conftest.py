import os
import pytest

from dotenv import load_dotenv

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.engine import URL

from examples.models._base import Base


def pytest_addoption(parser):
    parser.addoption(
        "--sqlecho",
        action="store_true",
        default=False,
        help="Show SQLAlchemy SQL echo",
    )


@pytest.fixture(scope="session")
def sqlecho(request) -> bool:
    return request.config.getoption("--sqlecho")


@pytest.fixture(scope="session")
def engine(sqlecho: bool) -> Engine:
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
        echo=sqlecho,  # show sql execute log
        future=True,
        pool_size=20,
        max_overflow=20,
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
            query = sa.text(f'TRUNCATE TABLE "{table.name}" RESTART IDENTITY CASCADE')

            db.execute(query)

        if engine.dialect.name == "postgresql":
            db.execute(sa.text("SET CONSTRAINTS ALL IMMEDIATE"))

        db.commit()

    Base.teardown_session()
