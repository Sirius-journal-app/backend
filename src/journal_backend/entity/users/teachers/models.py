from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from journal_backend.database.base import Base
from journal_backend.entity.users.mixins import UserColumnsMixin

if TYPE_CHECKING:
    from journal_backend.entity.classes.models import Class


class Teacher(Base, UserColumnsMixin):  # type: ignore[misc]
    __tablename__ = "teachers"

    qualification: Mapped[str] = mapped_column()
    education: Mapped[str] = mapped_column()

    competencies: Mapped[list["Competence"]] = relationship(back_populates="teacher")
    classes: Mapped[list["Class"]] = relationship(back_populates="teacher")


class Subject(Base):  # type: ignore[misc]
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))

    classes: Mapped[list["Class"]] = relationship(back_populates="subject")
    # People who are competent for the subject
    competents: Mapped[list["Competence"]] = relationship(back_populates="subjects")


class Competence(Base):  # type: ignore[misc]
    __tablename__ = "competencies"

    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id", ondelete="CASCADE"))
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"))

    teacher: Mapped["Teacher"] = relationship(back_populates="competencies")
    subject: Mapped["Subject"] = relationship(back_populates="competents")

    __table_args__ = (
        PrimaryKeyConstraint("teacher_id", "subject_id"),
    )
