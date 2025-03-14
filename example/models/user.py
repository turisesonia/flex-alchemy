import typing as t
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixin import TimestampMixin
from .user_permission import UserPermission


if t.TYPE_CHECKING:
    from .permission import Permission


class User(Base, TimestampMixin):
    __tablename__ = "users"
    __repr_attrs__ = ("id", "email", "name", "enable")

    name: Mapped[str] = mapped_column(sa.String(50))
    email: Mapped[str] = mapped_column(sa.String(), unique=True)
    password: Mapped[str] = mapped_column(sa.String())
    enable: Mapped[bool] = mapped_column(sa.Boolean(), default=True)

    permissions: Mapped[t.List["Permission"]] = relationship(
        secondary=UserPermission, back_populates="users"
    )
