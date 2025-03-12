import typing as t
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixin import TimestampMixin


class Permission(Base, TimestampMixin):
    __tablename__ = "permissions"

    __repr_attrs__ = ("id", "name")

    name: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    description: Mapped[t.Optional[str]] = mapped_column(sa.String(255), nullable=True)
