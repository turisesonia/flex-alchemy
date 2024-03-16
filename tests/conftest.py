import pytest

from alembic.config import Config
from alembic.command import upgrade, downgrade

from sqlalchemy import create_engine
from faker import Faker
from tests.models import Base


@pytest.fixture
def faker() -> Faker:
    return Faker()


@pytest.fixture(scope="session", autouse=True)
def _test_session():
    alembic_cfg = Config("tests/database/alembic.ini")

    upgrade(alembic_cfg, "head")

    # set_up: fill table at beginning of scope
    # populate_purchase_table_with_data(db, data)

    Base.set_engine(
        create_engine(
            "sqlite:///tests/database/test.db",
            echo=False,  # show sql execute log
            pool_size=20,
            pool_recycle=3600,  # pool close connection time
        )
    )

    # yield, to let all tests within the scope run
    yield

    Base.remove_scoped_session()

    downgrade(alembic_cfg, "base")
