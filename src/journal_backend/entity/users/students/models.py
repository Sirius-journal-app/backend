from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from journal_backend.database.base import Base
from journal_backend.entity.users.mixins import UserColumnsMixin

if TYPE_CHECKING:
    from journal_backend.entity.academic_reports.models import AcademicReport


class Student(Base, UserColumnsMixin):  # type: ignore[misc]
    __tablename__ = "students"

    admission_year: Mapped[int] = mapped_column()
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="SET NULL"))

    group: Mapped["Group"] = relationship(back_populates="students")
    academic_reports: Mapped[list['AcademicReport']] = relationship(back_populates='student')


class Group(Base):  # type: ignore[misc]
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()

    students: Mapped[list["Student"]] = relationship(back_populates="group")
