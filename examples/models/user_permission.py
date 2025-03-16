import typing as t
import uuid
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ._base import Base


if t.TYPE_CHECKING:
    from .user import User
    from .permission import Permission


# class UserPermission(Base):
#     __tablename__ = "user_permissions"

#     __repr_attrs__ = ("id", "user_id", "permission_id")

#     user_id: Mapped[uuid.UUID] = mapped_column(sa.Uuid(), sa.ForeignKey("users.id"))
#     permission_id: Mapped[uuid.UUID] = mapped_column(
#         sa.Uuid(), sa.ForeignKey("permissions.id")
#     )

#     user: Mapped["User"] = relationship("User", back_populates="permissions")
#     permission: Mapped["Permission"] = relationship(
#         "Permission", back_populates="users"
#     )


UserPermission = sa.Table(
    "user_permissions",
    Base.metadata,
    sa.Column("user_id", sa.ForeignKey("users.id"), primary_key=True),
    sa.Column("permission_id", sa.ForeignKey("permissions.id"), primary_key=True),
)
