from typing import List

from sqlalchemy import (
    BigInteger,
    Integer,
    SmallInteger,
    String,
    Boolean,
    Numeric,
    ForeignKey,
)
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
    __repr_attrs__ = ("id", "email", "name")

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True
    )
    email: Mapped[str] = mapped_column(String(), unique=True)
    password: Mapped[str] = mapped_column(String())
    name: Mapped[str] = mapped_column(String(50))
    state: Mapped[bool] = mapped_column(Boolean(), default=True)

    orders: Mapped[List["Order"]] = relationship(back_populates="user")


class Order(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "orders"
    __repr_attrs__ = ("id", "uuid", "cost")

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(BigInteger(), ForeignKey("users.id"))
    uuid: Mapped[str] = mapped_column(String(), unique=True)
    price: Mapped[float] = mapped_column(Numeric(10, 4), default=0)
    cost: Mapped[float] = mapped_column(Numeric(10, 4), default=0)
    state: Mapped[int] = mapped_column(SmallInteger())

    user: Mapped[User] = relationship(back_populates="orders")
