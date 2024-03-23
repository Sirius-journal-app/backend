from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampColumnsMixin:
    """Add `created_on` and `updated_on` columns to the model."""

    created_on: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_on: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=datetime.now
    )
