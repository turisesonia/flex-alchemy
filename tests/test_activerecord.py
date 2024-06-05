import math

from typing import Sequence
from sqlalchemy import select, insert, inspect
from sqlalchemy.orm import Session
from sqlalchemy.engine.row import Row
from sqlalchemy.engine.cursor import CursorResult

from .models import User, Project


def test_create(faker, email: str, name: str, session: Session):
    user = User.create(email=email, name=name, password=faker.password())

    assert isinstance(user, User)
    assert user.email == email
    assert user.name == name

    with session as db:
        u = db.scalar(select(User).where(User.id == user.id))

        assert isinstance(u, User)


def test_save(faker, email: str, name: str, session: Session):
    user = User(email=email, name=name, password=faker.password())

    user.save()

    assert isinstance(user, User)
    assert user.email == email
    assert user.name == name

    with session as db:
        u = db.scalar(select(User).where(User.id == user.id))

        assert isinstance(u, User)


def test_find(faker, email: str, name: str):
    user_id = User.create(email=email, name=name, password=faker.password()).id

    user = User.find(user_id)

    assert isinstance(user, User)
    assert user.email == email
    assert user.name == name


def test_find_with_string_uuid(faker, name: str):
    uuid = faker.uuid4()

    Project.create(uuid=uuid, name=name)

    project = Project.find(uuid)

    assert isinstance(project, Project)
    assert project.name == name


def test_select_specific_fields(faker, email: str, name: str):
    User.create(email=email, name=name, password=faker.password())

    user = (
        User.select(User.name, User.email)
        .where(User.email == email)
        .first(specific_fields=True)
    )

    assert isinstance(user, Row)
    assert user.name == name
    assert user.email == email

    user = User.select(User).where(User.email == email).first()
    assert isinstance(user, User)

    user_email = User.select(User.email).where(User.email == email).first()
    assert isinstance(user_email, str)
    assert user_email == email


def test_where(faker, email: str, name: str):
    User.create(email=email, name=name, password=faker.password())

    user = User.where(User.email == email).first()

    assert isinstance(user, User)
    assert user.email == email
    assert user.name == name


def test_model_save(faker, email: str, name: str):
    old_password = faker.password()
    new_password = faker.password()

    user = User.create(email=email, name=name, password=old_password)

    assert user.password == old_password

    user.password = new_password
    user.save()

    assert user.password == new_password


def test_all(faker, email: str, name: str):
    User.create(email=email, name=name, password=faker.password())

    users = User.all()
    assert isinstance(users, Sequence)

    for user in users:
        assert isinstance(user, User)


def test_paginate(faker, session: Session):
    total = faker.pyint(max_value=300)
    page = 1
    per_page = 15

    with session as db:
        # seeding
        db.execute(
            insert(User),
            [
                {
                    "name": faker.name(),
                    "email": f"{i}_{faker.email()}",
                    "password": faker.password(),
                }
                for i in range(total)
            ],
        )

        db.commit()

    pagination = User.paginate(page, per_page)

    assert pagination["total"] == total
    assert pagination["per_page"] == per_page
    assert pagination["current_page"] == page
    assert pagination["last_page"] == math.ceil(total / per_page)
    assert len(pagination["data"]) == per_page if total >= per_page else total

    for user in pagination["data"]:
        isinstance(user, User)


def test_insert_single(faker):
    values = {
        "name": faker.name(),
        "email": faker.email(),
        "password": faker.password(),
    }

    User.values(values).insert()

    user = User.first()
    assert isinstance(user, User)

    assert user.name == values["name"]
    assert user.email == values["email"]
    assert user.password == values["password"]


def test_insert_multiple(faker):
    total = 10

    User.values(
        [
            {
                "name": faker.name(),
                "email": faker.email(),
                "password": faker.password(),
            }
            for _ in range(total)
        ]
    ).insert()

    users = User.all()

    assert len(users) == total
    for user in users:
        assert isinstance(user, User)


def test_update(faker):
    # seed
    User.values(
        [
            {
                "name": faker.name(),
                "email": faker.email(),
                "password": faker.password(),
            }
            for _ in range(5)
        ]
    ).insert()

    updated = {"name": "updated_name"}

    User.values(name=updated["name"]).update()

    for user in User.all():
        assert user.name == updated["name"]


def test_model_delete(faker, email: str, name: str, session: Session):
    user = User.create(email=email, name=name, password=faker.password())
    user_id = user.id

    user.delete()

    assert User.find(user_id) is None

    with session as db:
        user_ = db.execute(select(User).where(User.id == user_id)).scalars().first()

        assert user_ is None


def test_model_delete_with_customize_primary_key(faker, name: str, session: Session):
    uuid = faker.uuid4()

    project = Project.create(uuid=uuid, name=name)

    assert isinstance(project, Project)

    project.delete()

    assert Project.find(uuid) is None

    with session as db:
        assert (
            db.execute(select(Project).where(Project.uuid == uuid)).scalars().first()
            is None
        )


def test_where_delete(faker, name: str, email: str):
    user = User.create(
        name=name,
        email=email,
        password=faker.password(),
    )

    result = User.where(User.email == email).delete()

    assert isinstance(result, CursorResult)
    assert not inspect(user).persistent

    # query the user is not exists
    user = User.where(User.email == email).first()
    assert user is None


# def test_model_soft_delete_self(faker, email: str, name: str):
#     user = User.create(email=email, name=name, password=faker.password())

#     order = Order.create(
#         user=user,
#         uuid=faker.uuid4(),
#         price=faker.pyfloat(),
#         cost=faker.pyfloat(),
#         state=1,
#     )

#     assert isinstance(order, Order)
#     assert isinstance(order.user, User)

#     uid = order.uuid
#     order.delete()

#     deleted = Order.where(Order.uuid == uid).first()
#     assert deleted is None

#     trashed = Order.where(Order.uuid == uid).first(with_trashed=True)
#     assert isinstance(trashed, Order)


# def test_force_delete_soft_delete_self(faker, email: str, name: str):
#     user = User.create(email=email, name=name, password=faker.password())

#     order = Order.create(
#         user=user,
#         uuid=faker.uuid4(),
#         price=faker.pyfloat(),
#         cost=faker.pyfloat(),
#         state=1,
#     )

#     assert isinstance(order, Order)
#     assert isinstance(order.user, User)

#     uid = order.uuid
#     order.delete(force=True)

#     deleted = Order.where(Order.uuid == uid).first()
#     assert deleted is None

#     trashed = Order.where(Order.uuid == uid).first(with_trashed=True)
#     assert trashed is None
