import os
import pytest

from dotenv import load_dotenv

from sqlalchemy import insert, create_engine, Engine
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
    return sessionmaker(engine, future=True)


@pytest.fixture
def seed_users(faker, session: Session):
    from examples.models import User

    values = [
        {
            "name": faker.name(),
            "email": faker.email(),
            "password": faker.password(),
            "enable": num % 2 == 0,
        }
        for num in range(10)
    ]

    with session() as db:
        stmt = insert(User).values(values)

        db.execute(stmt)
        db.commit()


@pytest.fixture
def seed_permissions(session: Session):
    from examples.models import Permission

    values = [
        {"name": "create_user"},
        {"name": "update_user"},
        {"name": "delete_user"},
    ]

    stmt = insert(Permission).values(values)

    with session() as db:
        db.execute(stmt)
        db.commit()


@pytest.fixture(autouse=True)
def bind_scoped_session(engine: Engine):
    import sqlalchemy as sa

    Base.make_session(engine)

    yield

    session = Base._session

    if engine.dialect.name == "postgresql":
        session.execute(sa.text("SET CONSTRAINTS ALL DEFERRED"))

    for table in reversed(Base.metadata.sorted_tables):
        query = sa.text(f'TRUNCATE TABLE "{table.name}" RESTART IDENTITY CASCADE')
        session.execute(query)

    if engine.dialect.name == "postgresql":
        session.execute(sa.text("SET CONSTRAINTS ALL IMMEDIATE"))

    session.commit()

    Base.teardown_session()
