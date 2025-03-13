import pytest
import typing as t

from example.models import User


@pytest.fixture
def user_data(faker) -> dict:
    return {
        "name": faker.name(),
        "email": faker.email(),
        "password": faker.password(),
    }


def test_create(user_data: dict):
    user = User.create(**user_data)

    assert isinstance(user, User)
    assert user.name == user_data["name"]
    assert user.email == user_data["email"]
    assert user.password == user_data["password"]

    user_find = User.find(user.id)

    assert isinstance(user_find, User)
    assert user_find is user


def test_save(user_data: dict):
    user = User(**user_data)

    user.save()

    assert isinstance(user, User)
    assert user.name == user_data["name"]
    assert user.email == user_data["email"]
    assert user.password == user_data["password"]


def test_find(user_data: dict):
    created = User.create(**user_data)

    user = User.find(created.id)
    assert isinstance(user, User)
    assert user.name == user_data["name"]
    assert user.email == user_data["email"]
    assert user.password == user_data["password"]
