import typing as t
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ._base import Base
from ._mixin import TimestampMixin
from .user_permission import UserPermission


if t.TYPE_CHECKING:
    from .user import User


class Permission(Base, TimestampMixin):
    __tablename__ = "permissions"

    __repr_attrs__ = ("id", "name")

    name: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    description: Mapped[t.Optional[str]] = mapped_column(sa.String(255), nullable=True)

    users: Mapped[t.List["User"]] = relationship(
        secondary=UserPermission, back_populates="permissions"
    )
