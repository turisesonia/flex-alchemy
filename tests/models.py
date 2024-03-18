from typing import List
from datetime import datetime, date

from sqlalchemy import (
    func,
    BigInteger,
    Integer,
    SmallInteger,
    String,
    Boolean,
    Date,
    ForeignKey,
    TIMESTAMP,
    Index,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

from sqlalchemy_model import ActiveRecord, TimestampMixin, SoftDeleteMixin


class Base(DeclarativeBase, ActiveRecord):
    def __repr__(self) -> str:
        """Returns representation of the object"""

        return "{name}({attrs})".format(
            name=self.__class__.__name__,
            attrs=", ".join(
                f"{attr}={getattr(self, attr)}" for attr in self.__repr_attrs__
            ),
        )


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"
    __repr_attrs__ = ("id", "email", "name")

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True
    )
    email: Mapped[str] = mapped_column(String(), unique=True)
    password: Mapped[str] = mapped_column(String())
    name: Mapped[str] = mapped_column(String(50))
    deleted_at: Mapped[datetime] = mapped_column(TIMESTAMP(), nullable=True)
