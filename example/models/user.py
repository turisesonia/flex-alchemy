import typing as t
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixin import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"
    __repr_attrs__ = ("id", "email", "name")

    name: Mapped[str] = mapped_column(sa.String(50))
    email: Mapped[str] = mapped_column(sa.String(), unique=True)
    password: Mapped[str] = mapped_column(sa.String())
