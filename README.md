# Flex Alchemy

Use SQLAlchemy with Active Record pattern.

## Installation

```shell
pip install flex-alchemy
```

## Quick Start

1. Declare Models and inherit ActiveRecord

    ```python
    # models.py
    from sqlalchemy.orm import DeclarativeBase
    from sqlalchemy import String, BigInteger, Boolean
    from sqlalchemy.orm import Mapped, mapped_column
    from flex_alchemy import ActiveRecord

    class Base(DeclarativeBase, ActiveRecord):
        pass

    class User(Base):
        __tablename__ = "users"

        id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
        email: Mapped[str] = mapped_column(String(), unique=True)
        password: Mapped[str] = mapped_column(String())
        name: Mapped[str] = mapped_column(String(50))
        enable: Mapped[bool] = mapped_column(Boolean(), default=True)
    ```

2. Create SQLAlchemy Engine, and assign to session handler in `ActiveRecord`

    ```python
    # database.py
    from sqlalchemy import create_engine
    from models import Base

    engine = create_engine("sqlite:///:memory:")

    Base.make_session(engine)
    ```

3. Start using model to operate database!

    ```python
    from models import User

    users = User.all()
    # [User(id=1), User(id=2), ...]
    ```

4. Release session resource after use
    ```python
    from models import Base

    Base.teardown_session()
    ```

## Usage

#### Create Records

```python
# Option #1: Use class method `create`
user = User.create(
    name="John Doe",
    email="john.doe@example.com",
    password="secure_password"
)

# Option #2: Create model instance and call `save` method
user = User(
    name="Jane Doe",
    email="jane.doe@example.com",
    password="another_password"
)
user.save()
```

#### Query Records

```python
# find a record by primary key
user = User.find(1)

# find all records
all_users = User.all()

# find a record with specific columns
row = User.select(User.id, User.name, User.email).execute().first()

# find records with conditions
active_users = User.where(User.enable.is_(True)).execute().scalars().all()
```

#### Update Records

```python
# find a record and update it by calling `save` method
user = User.find(1)
user.name = "New Name"
user.save()

# Update multiple records with conditions
User.update(updated_at=datetime.now()).where(User.enalbe.is_(True)).execute()
```

#### Delete Records

```python
# delete a record by calling `delete` method
user = User.find(1)
user.delete()

# delete multiple records
User.destroy().where(User.enable.is_(False)).execute()
```

## Examples

### Use in FastAPI

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy import create_engine
from app.models import Base, User

engine = create_engine("postgresql://user:password@localhost/dbname")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Make scoped session with engine when FastAPI start
    """
    Base.make_session(engine)
    yield

def close_session():
    """
    cleanup scoped session after each request
    """
    yield
    Base.teardown_session()


app = FastAPI(
    title="MyApp",
    lifespan=lifespan,
    dependencies=[Depends(close_session)],
)

@app.get("/users")
def index():
    """get all users"""
    return User.all()

@app.get("/users/{id_}")
def show(id_: int):
    """get user by id"""
    return User.find(id_)

@app.post("/users")
def create(user_data: dict):
    """create a new user"""
    return User.create(user_data)
```

## Others

### Use Session instead of Scoped Session

`flex-alchemy` provides a way to use `Session` instead of `ScopedSession` by pass a `Session` instance to `execute` method.


```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine("sqlite:///:memory:")

with Session(engine) as session:
    # find all users
    User.all(session=session)

    # find a user by primary key
    User.find(1, session=session)

    # create a new user
    User.create({
        "name": "New User",
        "email": "example@mail.com"
        "password": "password"
    }, session=session)

    user = User(
        name="New User",
        email="example@mail.com",
        password="password"
    )
    user.save(session=session)

    User.where(User.enable.is_(True)).execute(session=session).scalars().all()

    ... etc
```