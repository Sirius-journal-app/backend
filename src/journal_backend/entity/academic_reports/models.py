from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from journal_backend.database.base import Base
from journal_backend.entity.academic_reports.enums import Graduation

if TYPE_CHECKING:
    from journal_backend.entity.classes.models import Class
    from journal_backend.entity.users.students.models import Student


class AcademicReport(Base):  # type: ignore[misc]
    __tablename__ = "academic_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="NO ACTION"))
    lesson_id = mapped_column(ForeignKey("classes.id", on_delete="NO ACTION"))
    is_attended: Mapped[bool] = mapped_column(default=False)
    grade: Mapped[Graduation] = mapped_column(nullable=True)

    student: Mapped['Student'] = relationship(back_populates='academic_reports', cascade="save-update")
    lesson: Mapped['Class'] = relationship(back_populates='academic_reports', cascade="save-update")
