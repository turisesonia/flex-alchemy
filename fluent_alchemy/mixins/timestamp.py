from datetime import datetime
from sqlalchemy import TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(), default=func.now(), nullable=True
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(), default=func.now(), nullable=True, onupdate=func.now()
    )
