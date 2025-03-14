import pytest

import sqlalchemy as sa
from sqlalchemy.orm import Session

from example.models import User, Permission


@pytest.fixture
def seed_users(faker, session: Session):
    values = [
        {
            "name": faker.name(),
            "email": faker.email(),
            "password": faker.password(),
            "enable": num % 2 == 0,
        }
        for num in range(10)
    ]

    stmt = sa.insert(User).values(values)

    session.execute(stmt)
    session.commit()


@pytest.fixture
def seed_permissions(session: Session):
    values = [
        {"name": "create_user"},
        {"name": "update_user"},
        {"name": "delete_user"},
    ]

    stmt = sa.insert(Permission).values(values)

    session.execute(stmt)
    session.commit()


def test_select(session: Session, seed_users):
    row = User.select(User.id, User.name).execute(session=session).first()

    assert isinstance(row, sa.engine.row.Row)
    assert hasattr(row, "id")
    assert hasattr(row, "name")

    assert not hasattr(row, "email")
    assert not hasattr(row, "password")
    assert not hasattr(row, "enable")

    assert isinstance(row.id, int)
    assert isinstance(row.name, str)


def test_first(session: Session, seed_users):
    user = User.first(session=session)

    assert isinstance(user, User)


def test_find(session: Session, seed_users):
    user = User.find(1, session=session)

    assert isinstance(user, User)

    assert not User.find(100, session=session)


def test_all(session: Session, seed_users):
    users = User.all(session=session)

    assert len(users) == 10

    for user in users:
        assert isinstance(user, User)


def test_create(faker, session: Session):
    data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "password": faker.password(),
    }

    user = User.create(data, session=session)

    assert isinstance(user, User)
    assert user.name == data["name"]
    assert user.email == data["email"]
    assert user.password == data["password"]


def test_where(session: Session, seed_users):
    users = User.where(User.enable.is_(True)).execute(session=session).scalars().all()

    assert len(users) == 5

    for user in users:
        assert isinstance(user, User)
        assert user.enable


def test_order_by(session: Session, seed_users):
    users = User.limit(5).execute(session=session).scalars().all()

    assert len(users) == 5

    for user in users:
        assert isinstance(user, User)


def test_limit(session: Session, seed_users):
    users = User.offset(5).execute(session=session).scalars().all()

    assert len(users) == 5
    assert users[0].id == 6


def test_insert(faker, session: Session):
    assert len(User.all(session=session)) == 0

    values = [
        {
            "name": faker.name(),
            "email": faker.email(),
            "password": faker.password(),
            "enable": True,
        }
        for _ in range(5)
    ]

    result = User.insert(values).returning(User).execute(session=session)

    # if set returning
    users = result.scalars().all()

    assert len(users) == 5

    for user in users:
        assert isinstance(user, User)


def test_update(faker, session: Session, seed_users):
    new_name = faker.name()

    # update all users
    User.update(name=new_name).execute(session=session)

    users = User.all(session=session)

    assert users

    for user in users:
        assert user.name == new_name


def test_update_with_where(faker, session: Session, seed_users):
    new_name = faker.name()

    # update all users
    User.update(name=new_name).where(User.enable.is_(True)).execute(session=session)

    users = User.all(session=session)

    assert users

    for user in users:
        if user.enable:
            assert user.name == new_name
        else:
            assert user.name != new_name


def test_update_by_save(faker, session: Session, seed_users):
    user = User.first(session=session)

    new_name = faker.name()
    assert user.name != new_name

    user.name = new_name
    user.save(session)

    assert User.find(user.id, session=session).name == new_name


def test_delete(session: Session, seed_users):
    user = User.first(session=session)

    email = user.email

    user.delete(session=session)

    assert len(User.all(session=session)) == 9
    assert (
        not User.where(User.email == email).execute(session=session).scalars().first()
    )


def test_destroy(session: Session, seed_users):
    assert len(User.all(session=session)) == 10

    User.destroy().execute(session=session)

    assert len(User.all(session=session)) == 0


def test_destroy_with_where(session: Session, seed_users):
    assert len(User.all(session=session)) == 10

    User.destroy().where(User.enable.is_(False)).execute(session=session)

    users = User.all(session=session)
    assert len(users) == 5

    for user in users:
        assert user.enable


def test_user_attach_permission(session, seed_users, seed_permissions):
    user = User.first(session)

    assert len(user.permissions) == 0

    user.permissions = Permission.all(session)
    user.save(session)

    assert len(user.permissions) == 3
