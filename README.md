# Fluent Alchemy

輕鬆流暢地使用 SQLAclhemy

- [Installation](#installation)
- [Quick start](#quick-start)
- [Features](#features)
- [Mixins](#mixins)
- [Examples](#examples)

## Installation

```shell
pip insall fluent-alchemy
```

## Quick start

1. 宣告 Models 並繼承 `ActiveRecord`

```python
# models.py
from sqlalchemy.orm import DeclarativeBase
from fluent_alchemy import ActiveRecord

class Base(DeclarativeBase, ActiveRecord):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    email: Mapped[str] = mapped_column(String(), unique=True)
    password: Mapped[str] = mapped_column(String())
    name: Mapped[str] = mapped_column(String(50))
    state: Mapped[bool] = mapped_column(Boolean())

```

2. 建立 SQLAclhemy Engine, 並指派給 `ActiveRecord` 內的 session handler

```python
from sqlalchemy import create_engine
from models import Base

engine = create_engine("sqlite://:memory:", echo=True)

Base.set_engine(engine)
```

3. 開始使用 model 操作 database !

```python
from models import User

users = User.all()
```

4. 使用完畢後，釋放 Session 資源

```python
from models import Base

Base.remove_scoped_session()
```

## Features

### Active Record
利用 `QueryBuilder` 來處理 SQLAlchemy 的 `select()` query statement

- Create

    ```python
    from models import User

    user = User.create(
        name="Justin",
        email="corey97@example.org",
        password="NioWe9Wn#+"
    )

    # or

    user = User(
        name="Justin",
        email="corey97@example.org",
        password="NioWe9Wn#+"
    )
    user.save()
    ```

- Read
    1. Find by id

        ```python
        user = User.find(1)
        ```

    2. 只回傳特定欄位

        ```python
        user = User.select(User.id, User.name, User.email).first()
        ```

    3. 透過 `where` 增加查詢條件

        ```python
        user = User.where(User.email == "corey97@example.org").first()
        ```

        ```python
        users = User.where(User.state.is_(True)).get()
        ```

- Update

    ```python
    user = User.find(1)
    user.passwod = "6xjVAY$p&D"

    user.save()
    ```

- Delete

    ```python
    user = User.find(1)
    user.delete()
    ```

- Pagenate

    ```python
    # setting page number and rows count per page
    pagination = User.paginate(page=1, per_page=15)

    """
    {
        "total": 100,
        "per_page": 15,
        "current_page": 1,
        "last_page": 7,
        "data": [ ... ], # ussers
    }
    """
    ```


## Mixins

### [`TimestampMixin`](./fluent_alchemy/mixins/timestamp.py)

讓指定的 Model class 繼承 `TimestampMixin`，讓該 Model 補上 `created_at`, `updated_at` 欄位。

```python
from fluent_alchemy import ActiveRecord, TimestampMixin

class Base(DeclarativeBase, ActiveRecord):
    pass

class User(Base, TimestampMixin):
    __tablename__ = "users"
    ...

###
user = User.find(1)

print(user.created_at)
print(user.updated_at)
```


### [`SoftDeleteMixin`](./fluent_alchemy/mixins/softdelete.py)

讓指定的 Model class 繼承 `SoftDeleteMixin`，就可以讓該 Model 擁有 Soft delete 的能力。

```python
from sqlalchemy.orm import DeclarativeBase
from fluent_alchemy import ActiveRecord, SoftDeleteMixin

class Base(DeclarativeBase, ActiveRecord):
    pass

class User(Base, SoftDeleteMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    email: Mapped[str] = mapped_column(String(), unique=True)
    password: Mapped[str] = mapped_column(String())
    name: Mapped[str] = mapped_column(String(50))
    state: Mapped[bool] = mapped_column(Boolean())
```

`SoftDeleteMixin` 會自動補上 `deleted_at` 欄位，依此欄位來處理 soft delete 的資料。

```python
deleted_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(), nullable=True)
```

設定完成後，之後對此 Model 進行 Query 時，會在 statement 內的 WHERE 條件自動加上 `deleted_at IS NULL`。

#### 查詢已被標記刪除的資料
```python
users_deleted = User.where(...).get(with_trashed=True)
```

#### 強制刪除 (Force delete)
```python
user = User.find(1)

user.delete(force=True)
```

## Examples

### 在 FastAPI 內使用

```python

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from app.models import BaseModel, User

def close_scoped_session():
    """
    Remove the scoped session at the enf of every request.
    """
    yield
    BaseModel.remove_scoped_session()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Set engine to the ScopedSessionHandler when FastAPI app started.
    """
    BaseModel.set_engine(engine)
    yield

app = FastAPI(
    title="MyApp",
    dependencies=[Depends(close_scoped_session)],
    lifespan=lifespan
)

@app.get("/users")
def index():
    return User.all()

```