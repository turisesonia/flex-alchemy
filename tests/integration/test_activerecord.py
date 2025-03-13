import pytest
import typing as t

from example.models import User, Permission


@pytest.fixture
def user_data(faker) -> dict:
    return {
        "name": faker.name(),
        "email": faker.email(),
        "password": faker.password(),
    }


@pytest.fixture
def seed_users(faker, session):
    values = [
        {
            "name": faker.name(),
            "email": faker.email(),
            "password": faker.password(),
        }
        for _ in range(10)
    ]

    User.insert(values, session=session)


@pytest.fixture
def seed_permissions(session):
    values = [
        {"name": "create_user"},
        {"name": "update_user"},
        {"name": "delete_user"},
    ]

    Permission.insert(values, session=session)


def test_user_crud(session, user_data: dict):
    user = User.create(user_data, session=session)

    assert isinstance(user, User)
    assert user.name == user_data["name"]
    assert user.email == user_data["email"]
    assert user.password == user_data["password"]

    # TODO - Add test for where, update, delete

    user_find = User.find(user.id)

    assert isinstance(user_find, User)
    assert user_find is user

    user.name = "New Name"
    user.save()

    assert user.name == "New Name"


def test_user_attach_permission(session, seed_users, seed_permissions):
    user = User.first(session)

    assert len(user.permissions) == 0

    user.permissions = Permission.all(session)
    user.save(session)

    assert len(user.permissions) == 3
