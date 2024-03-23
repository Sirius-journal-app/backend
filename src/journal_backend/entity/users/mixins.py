from datetime import date
from typing import Optional

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column


class UserColumnsMixin:
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    surname: Mapped[str] = mapped_column(String(64))
    date_of_birth: Mapped[Optional[date]] = mapped_column(DateTime(timezone=True))
    profile_photo_uri: Mapped[Optional[str]] = mapped_column()
    email: Mapped[str] = mapped_column(String(128), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(256))
