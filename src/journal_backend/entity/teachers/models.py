from typing import Optional

from sqlalchemy import ForeignKey, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from starlette.requests import Request

from journal_backend.database.base import Base
from journal_backend.entity.classes.models import Class
from journal_backend.entity.users.models import UserIdentity


class Teacher(Base):  # type: ignore[misc]
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(
        ForeignKey("user_identity.id", ondelete="CASCADE"),
        primary_key=True
    )
    qualification: Mapped[Optional[str]] = mapped_column()
    education: Mapped[Optional[str]] = mapped_column()

    identity: Mapped["UserIdentity"] = relationship(lazy="joined")
    competencies: Mapped[list["Subject"]] = relationship(
        back_populates="competents",
        secondary='competencies',
        lazy="joined"
    )
    classes: Mapped[list["Class"]] = relationship(back_populates="teacher")

    def __str__(self) -> str:
        return f"{self.identity}; competencies: {[c.subject.name for c in self.competencies]}"

    async def __admin_repr__(self, _: Request) -> str:
        return f"{self.identity.surname} {self.identity.name}"

    async def __admin_select2_repr__(self, _: Request) -> str:
        return f"<div>{self.identity.surname} {self.identity.name}</div>"


class Subject(Base):  # type: ignore[misc]
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)

    classes: Mapped[list["Class"]] = relationship(back_populates="subject")
    # People who are competent for the subject
    competents: Mapped[list["Teacher"]] = relationship(
        back_populates="competencies",
        secondary='competencies',
    )

    async def __admin_repr__(self, _: Request) -> str:
        return f"{self.name}"

    async def __admin_select2_repr__(self, _: Request) -> str:
        return f"<div>{self.name}</div>"


class Competence(Base):  # type: ignore[misc]
    __tablename__ = "competencies"

    teacher: Mapped["Teacher"] = relationship(lazy="joined")
    subject: Mapped["Subject"] = relationship(lazy="joined")

    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id", ondelete="CASCADE"))
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"))

    __table_args__ = (
        PrimaryKeyConstraint("teacher_id", "subject_id"),
    )

    async def __admin_repr__(self, _: Request) -> str:
        return f"{self.subject_id}"

    async def __admin_select2_repr__(self, _: Request) -> str:
        return f"<div>{self.subject_id}</div>"
