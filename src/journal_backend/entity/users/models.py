from datetime import date
from typing import Optional

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from starlette.requests import Request

from journal_backend.database.base import Base
from journal_backend.entity.users.enums import Role


class UserIdentity(Base):  # type:ignore[misc]
    __tablename__ = "user_identity"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    surname: Mapped[str] = mapped_column(String(64))
    # last_name: Mapped[str] = mapped_column(String(64))
    date_of_birth: Mapped[Optional[date]] = mapped_column(DateTime(timezone=True))
    profile_photo_uri: Mapped[Optional[str]] = mapped_column()
    email: Mapped[str] = mapped_column(
        String(length=320), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(length=1024), nullable=False
    )
    role: Mapped[Role] = mapped_column()
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # can be defined by the role (this is a stub for fastapi-users)
    is_superuser: bool = False

    async def __admin_repr__(self, _: Request) -> str:
        return f"{self.surname} {self.name}"
