import pytest

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy_model.builder import QueryBuilder

from .models import User


@pytest.fixture
def session(engine) -> Session:
    return sessionmaker(engine)
