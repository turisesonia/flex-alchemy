from typing import Optional
from datetime import datetime
from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from ..scopes.softdelete import SoftDeleteScope


class SoftDeleteMixin:
    deleted_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(), nullable=True)

    @classmethod
    def scope_registry(cls) -> SoftDeleteScope:
        return SoftDeleteScope()
