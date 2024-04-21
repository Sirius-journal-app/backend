from typing import Optional

from sqlalchemy import ForeignKey, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    competencies: Mapped[list["Competence"]] = relationship(
        back_populates="teacher",
        lazy="joined"
    )
    classes: Mapped[list["Class"]] = relationship(back_populates="teacher")


class Subject(Base):  # type: ignore[misc]
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)

    classes: Mapped[list["Class"]] = relationship(back_populates="subject")
    # People who are competent for the subject
    competents: Mapped[list["Competence"]] = relationship(back_populates="subject")


class Competence(Base):  # type: ignore[misc]
    __tablename__ = "competencies"

    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id", ondelete="CASCADE"))
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"))

    teacher: Mapped["Teacher"] = relationship(back_populates="competencies")
    subject: Mapped["Subject"] = relationship(back_populates="competents")

    __table_args__ = (
        PrimaryKeyConstraint("teacher_id", "subject_id"),
    )
