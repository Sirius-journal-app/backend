from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, ForeignKeyConstraint, Interval
from sqlalchemy.orm import Mapped, mapped_column, relationship
from starlette.requests import Request

from journal_backend.database.base import Base

if TYPE_CHECKING:
    from journal_backend.entity.students.models import AcademicReport, Group
    from journal_backend.entity.teachers.models import Subject, Teacher

DEFAULT_CLASS_DURATION = timedelta(minutes=60 * 1.5)


class Class(Base):  # type: ignore[misc]
    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(primary_key=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    duration: Mapped[timedelta] = mapped_column(
        Interval(native=True),
        default=DEFAULT_CLASS_DURATION
    )
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete='CASCADE'))
    teacher_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("teachers.id", ondelete='SET NULL')
    )
    subject_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("subjects.id", ondelete='SET NULL')
    )
    classroom_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("classrooms.id", ondelete="SET NULL")
    )

    academic_reports: Mapped[list["AcademicReport"]] = relationship(back_populates="class_")
    group: Mapped["Group"] = relationship(back_populates="classes", lazy='joined')
    teacher: Mapped["Teacher"] = relationship(back_populates="classes", lazy='joined')
    subject: Mapped["Subject"] = relationship(back_populates="classes", lazy='joined')
    classroom: Mapped["Classroom"] = relationship(back_populates="classes", lazy='joined')

    __table_args__ = (
        ForeignKeyConstraint(
            [teacher_id, subject_id],
            ["competencies.teacher_id", "competencies.subject_id"],
            ondelete="SET NULL"
        ),
    )

    async def __admin_repr__(self, _: Request) -> str:
        return f"""Group: {self.group.name};
Subject: {self.subject.name if self.subject else None};
Starts at: {self.starts_at}"""

    async def __admin_select2_repr__(self, _: Request) -> str:
        return f"""<div>Group: {self.group.name};
Subject: {self.subject.name if self.subject else None};
Starts at: {self.starts_at}</div>"""


class Classroom(Base):  # type: ignore[misc]
    __tablename__ = "classrooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    classes: Mapped[list["Class"]] = relationship(back_populates="classroom")

    async def __admin_repr__(self, _: Request) -> str:
        return f"{self.name}"

    async def __admin_select2_repr__(self, _: Request) -> str:
        return f"<div>{self.name}</div>"
