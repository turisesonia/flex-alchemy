import sqlalchemy as sa

from examples.models import User, Permission


def test_select(seed_users):
    row = User.select(User.id, User.name).execute().first()

    assert isinstance(row, sa.engine.row.Row)
    assert hasattr(row, "id")
    assert hasattr(row, "name")

    assert not hasattr(row, "email")
    assert not hasattr(row, "password")
    assert not hasattr(row, "enable")

    assert isinstance(row.id, int)
    assert isinstance(row.name, str)


def test_first(seed_users):
    user = User.first()

    assert isinstance(user, User)


def test_find(seed_users):
    user = User.find(1)

    assert isinstance(user, User)

    assert not User.find(100)


def test_all(seed_users):
    users = User.all()

    assert len(users) == 10

    for user in users:
        assert isinstance(user, User)


def test_create(faker):
    data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "password": faker.password(),
    }

    user = User.create(data)

    assert isinstance(user, User)
    assert user.name == data["name"]
    assert user.email == data["email"]
    assert user.password == data["password"]


def test_where(seed_users):
    users = User.where(User.enable.is_(True)).execute().scalars().all()

    assert len(users) == 5

    for user in users:
        assert isinstance(user, User)
        assert user.enable


def test_order_by(seed_users):
    users = User.limit(5).execute().scalars().all()

    assert len(users) == 5

    for user in users:
        assert isinstance(user, User)


def test_limit(seed_users):
    users = User.offset(5).execute().scalars().all()

    assert len(users) == 5
    assert users[0].id == 6


def test_insert(faker):
    assert len(User.all()) == 0

    values = [
        {
            "name": faker.name(),
            "email": faker.email(),
            "password": faker.password(),
            "enable": True,
        }
        for _ in range(5)
    ]

    result = User.insert(values).returning(User).execute()

    # if set returning
    users = result.scalars().all()

    assert len(users) == 5

    for user in users:
        assert isinstance(user, User)


def test_update(faker, seed_users):
    new_name = faker.name()

    # update all users
    User.update(name=new_name).execute()

    users = User.all()

    assert users

    for user in users:
        assert user.name == new_name


def test_update_with_where(faker, seed_users):
    new_name = faker.name()

    # update all users
    User.update(name=new_name).where(User.enable.is_(True)).execute()

    users = User.all()

    assert users

    for user in users:
        if user.enable:
            assert user.name == new_name
        else:
            assert user.name != new_name


def test_update_by_save(faker, seed_users):
    user = User.first()

    new_name = faker.name()
    assert user.name != new_name

    user.name = new_name
    user.save()

    assert (
        User.find(
            user.id,
        ).name
        == new_name
    )


def test_delete(seed_users):
    user = User.first()

    email = user.email

    user.delete()

    assert len(User.all()) == 9
    assert not User.where(User.email == email).execute().scalars().first()


def test_destroy(seed_users):
    assert len(User.all()) == 10

    User.destroy().execute()

    assert len(User.all()) == 0


def test_destroy_with_where(seed_users):
    assert len(User.all()) == 10

    User.destroy().where(User.enable.is_(False)).execute()

    users = User.all()
    assert len(users) == 5

    for user in users:
        assert user.enable


def test_user_attach_permission(faker, seed_permissions):
    permissions = Permission.all()

    user = User(
        name=faker.name(),
        email=faker.email(),
        password=faker.password(),
        permissions=permissions,
    )

    user.save()

    assert len(user.permissions) == 3

    User.first()


def test_execute(faker):
    name = faker.name()
    email = faker.email()
    password = faker.password()

    insert_stmt = sa.insert(User).values(
        name=name,
        email=email,
        password=password,
    )

    User.execute(insert_stmt)
    User._session.commit()

    user = User.where(User.email == email).execute().scalars().first()

    assert isinstance(user, User)

    assert user.name == name
    assert user.email == email
    assert user.password == password
