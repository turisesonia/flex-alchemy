import pytest

from typing import Sequence
from .models import User, Order


@pytest.fixture
def name(faker):
    return faker.name()


@pytest.fixture
def email(faker):
    return faker.email()


def test_create(email, name):
    user = User.create(email=email, name=name, password="password")

    assert isinstance(user, User)
    assert user.email == email
    assert user.name == name


def test_find(email, name):
    user = User.create(email=email, name=name, password="password")

    user = User.find(user.id)

    assert isinstance(user, User)
    assert user.email == email
    assert user.name == name


def test_save(email, name):
    user = User(email=email, name=name, password="password")

    user.save()

    assert isinstance(user.id, int)
    assert isinstance(user, User)
    assert user.email == email
    assert user.name == name


def test_where(email, name):
    User.create(
        email=email,
        name=name,
        password="password",
    )

    user = User.where(User.email == email).first()

    assert isinstance(user, User)
    assert user.email == email
    assert user.name == name


def test_all(email, name):
    User.create(
        email=email,
        name=name,
        password="password",
    )

    users = User.all()
    assert isinstance(users, Sequence)

    for user in users:
        assert isinstance(user, User)


def test_soft_delete(faker, email, name):
    user = User.create(
        email=email,
        name=name,
        password="password",
    )

    order = Order.create(
        user=user,
        uuid=faker.uuid4(),
        price=faker.pyfloat(),
        cost=faker.pyfloat(),
        state=1,
    )

    assert isinstance(order, Order)
    assert isinstance(order.user, User)

    uid = order.uuid
    order.delete()

    deleted = Order.where(Order.uuid == uid).first()
    assert deleted is None

    trashed = Order.where(Order.uuid == uid).first(with_trashed=True)
    assert isinstance(trashed, Order)


def test_force_delete_soft_delete(faker, email, name):
    user = User.create(
        email=email,
        name=name,
        password="password",
    )

    order = Order.create(
        user=user,
        uuid=faker.uuid4(),
        price=faker.pyfloat(),
        cost=faker.pyfloat(),
        state=1,
    )

    assert isinstance(order, Order)
    assert isinstance(order.user, User)

    uid = order.uuid
    order.delete(force=True)

    deleted = Order.where(Order.uuid == uid).first()
    assert deleted is None

    trashed = Order.where(Order.uuid == uid).first(with_trashed=True)
    assert trashed is None
