from typing import Optional
from datetime import datetime
from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.hybrid import hybrid_property


class SoftDeleteMixin:
    deleted_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(), nullable=True)

    @hybrid_property
    def without_trashed(self):
        return self.deleted_at.is_(None)
