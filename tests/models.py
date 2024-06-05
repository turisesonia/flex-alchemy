from typing import List

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from fluent_alchemy import ActiveRecord, TimestampMixin, SoftDeleteMixin


class Base(DeclarativeBase, ActiveRecord):
    def __repr__(self) -> str:
        """Returns representation of the object"""

        return "{name}({attrs})".format(
            name=self.__class__.__name__,
            attrs=", ".join(
                f"{attr}={getattr(self, attr)}" for attr in self.__repr_attrs__
            ),
        )


class User(Base, TimestampMixin):
    __tablename__ = "users"
    __repr_attrs__ = ("id", "email", "name", "state")

    id: Mapped[int] = mapped_column(
        sa.BigInteger().with_variant(sa.Integer, "sqlite"), primary_key=True
    )
    email: Mapped[str] = mapped_column(sa.String(), unique=True)
    password: Mapped[str] = mapped_column(sa.String())
    name: Mapped[str] = mapped_column(sa.String(50))
    state: Mapped[bool] = mapped_column(sa.Boolean(), default=True)

    orders: Mapped[List["Order"]] = relationship(back_populates="user")


class Order(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "orders"
    __repr_attrs__ = ("id", "uuid", "cost")

    id: Mapped[int] = mapped_column(
        sa.BigInteger().with_variant(sa.Integer, "sqlite"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(sa.BigInteger(), sa.ForeignKey("users.id"))
    uuid: Mapped[str] = mapped_column(sa.String(), unique=True)
    price: Mapped[float] = mapped_column(sa.Numeric(10, 4), default=0)
    cost: Mapped[float] = mapped_column(sa.Numeric(10, 4), default=0)
    state: Mapped[int] = mapped_column(sa.SmallInteger())

    user: Mapped[User] = relationship(back_populates="orders")


class Project(Base, TimestampMixin):
    __tablename__ = "projects"
    __repr_attrs__ = ("uuid", "name")
    __primary_key__ = "uuid"

    uuid: Mapped[str] = mapped_column(sa.Uuid(as_uuid=False), primary_key=True)
    name: Mapped[str] = mapped_column(sa.String())
