from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from starlette.requests import Request

from journal_backend.database.base import Base
from journal_backend.entity.students.enums import Graduation
from journal_backend.entity.users.models import UserIdentity

if TYPE_CHECKING:
    from journal_backend.entity.classes.models import Class


class Student(Base):  # type: ignore[misc]
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(
        ForeignKey("user_identity.id", ondelete="CASCADE"),
        primary_key=True
    )
    group_id: Mapped[Optional[int]] = mapped_column(ForeignKey("groups.id", ondelete="SET NULL"))

    identity: Mapped["UserIdentity"] = relationship(lazy="joined")
    group: Mapped["Group"] = relationship(back_populates="students", lazy="joined")
    academic_reports: Mapped[list["AcademicReport"]] = relationship(back_populates='student')


class Group(Base):  # type: ignore[misc]
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    admission_year: Mapped[int] = mapped_column()

    students: Mapped[list["Student"]] = relationship(back_populates="group")
    classes: Mapped[list["Class"]] = relationship(back_populates="group")

    def __str__(self) -> str:
        return self.name

    async def __admin_repr__(self, _: Request) -> str:
        return f"{self.name}"


class AcademicReport(Base):  # type: ignore[misc]
    __tablename__ = "academic_reports"

    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="NO ACTION"))
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id", ondelete="NO ACTION"))
    is_attended: Mapped[bool] = mapped_column(default=False)
    grade: Mapped[Graduation] = mapped_column(nullable=True)

    student: Mapped["Student"] = relationship(
        back_populates='academic_reports',
        cascade="save-update",
        lazy='joined',
    )
    class_: Mapped["Class"] = relationship(
        back_populates='academic_reports',
        cascade="save-update",
        lazy='joined'
    )

    __table_args__ = (
        PrimaryKeyConstraint("student_id", "class_id"),
    )
