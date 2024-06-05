import os
import pytest

from faker import Faker
from pytest_mock import MockerFixture
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from tests.models import Base


@pytest.fixture
def mocker(mocker: MockerFixture) -> MockerFixture:
    return mocker


@pytest.fixture
def faker() -> Faker:
    return Faker()


@pytest.fixture(scope="session")
def engine() -> Engine:
    return create_engine("sqlite:///:memory:")


@pytest.fixture
def session(engine) -> Session:
    return sessionmaker(engine)()


@pytest.fixture(autouse=True)
def _test_session(engine):
    APP_DEBUG: bool = (
        True if os.getenv("APP_DEBUG", "false").lower() == "true" else False
    )

    engine.echo = APP_DEBUG

    Base.metadata.create_all(engine)
    Base.set_engine(engine)

    # yield, to let all tests within the scope run
    yield

    Base.remove_scoped_session()
    Base.metadata.drop_all(engine)


@pytest.fixture
def name(faker):
    return faker.name()


@pytest.fixture
def email(faker):
    return faker.email()


# @pytest.fixture(scope="session", autouse=True)
# def _test_session():
#     alembic_cfg = Config("tests/database/alembic.ini")

#     upgrade(alembic_cfg, "head")

#     # set_up: fill table at beginning of scope
#     # populate_purchase_table_with_data(db, data)
#     Base.set_engine(
#         create_engine(
#             # "sqlite:///tests/database/test.db",
#             "sqlite:///tests/database/test.db",
#             echo=False,  # show sql execute log
#             pool_size=20,
#             pool_recycle=3600,  # pool close connection time
#         )
#     )

#     # yield, to let all tests within the scope run
#     yield

#     Base.remove_scoped_session()

#     downgrade(alembic_cfg, "base")
