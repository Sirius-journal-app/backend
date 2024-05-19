from dataclasses import dataclass

from journal_backend.entity.academic_reports.enums import Graduation
from journal_backend.entity.academic_reports.models import AcademicReport
from journal_backend.entity.classes.dto import ClassRead, to_read_dto


@dataclass
class AcademicReportRead:
    id: int
    student: str
    is_attended: bool
    grade: Graduation
    lesson: ClassRead


def build_academic_reports_response(academic_reports: list[AcademicReport]) -> list[AcademicReportRead]:
    resp = []
    for report in academic_reports:
        resp.append(AcademicReportRead(
            id=report.id,
            student=report.student.identity.name,
            is_attended=report.is_attended,
            grade=report.grade,
            lesson=to_read_dto(class_=report.lesson),
        ))
    return resp
