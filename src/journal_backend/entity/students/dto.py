from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Optional

from pydantic import EmailStr

from journal_backend.entity.classes.dto import ClassRead, to_read_dto
from journal_backend.entity.students.enums import Graduation
from journal_backend.entity.students.models import Student, AcademicReport


@dataclass
class Group:
    id: int
    name: str
    admission_year: int


@dataclass(frozen=True, kw_only=True)
class StudentRead:
    id: int
    name: str
    surname: str
    email: str
    profile_photo_uri: str
    birth_date: Optional[datetime] = None
    group: Optional[Group] = None
    is_verified: bool


@dataclass(kw_only=True)
class StudentCreate:
    name: str
    surname: str
    date_of_birth: Optional[date] = None
    email: EmailStr
    password: str
    group_name: str


@dataclass
class StudentUpdate:
    param: str
    value: Any


@dataclass(frozen=True, kw_only=True)
class AuthResponse:
    token: str
    student: StudentRead


def model_to_read_dto(student: Student) -> StudentRead:
    group = None
    if student.group:
        group = Group(
            id=student.group.id,
            name=student.group.name,
            admission_year=student.group.admission_year,
        )

    return StudentRead(
        id=student.identity.id,
        name=student.identity.name,
        surname=student.identity.surname,
        email=student.identity.email,
        profile_photo_uri=student.identity.profile_photo_uri,
        birth_date=student.identity.date_of_birth,
        group=group,
        is_verified=student.identity.is_verified,
    )


@dataclass
class AcademicReportCreate:
    student_id: int
    class_id: int
    is_attended: bool
    grade: Optional[Graduation] = None


@dataclass
class AcademicReportRead:
    id: int
    student: str
    class_: ClassRead
    is_attended: bool
    grade: Optional[Graduation] = None


def build_academic_reports_response(academic_reports: list[AcademicReport]) -> list[AcademicReportRead]:
    resp = []
    for report in academic_reports:
        resp.append(AcademicReportRead(
            id=report.id,
            student=report.student.identity.name,
            is_attended=report.is_attended,
            grade=report.grade,
            class_=to_read_dto(class_=report.class_),
        ))
    return resp
