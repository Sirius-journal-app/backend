from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr

from journal_backend.entity.students.models import Student


@dataclass
class Group:
    id: int
    name: str
    admission_year: int


@dataclass(frozen=True, kw_only=True)
class StudentRead:
    name: str
    surname: str
    email: str
    profile_photo_uri: str
    birth_date: Optional[datetime] = None
    group: Optional[Group] = None
    is_verified: bool


class StudentCreate(BaseModel):
    name: str
    surname: str
    date_of_birth: Optional[date] = None
    email: EmailStr
    password: str
    group_name: str = ""


class StudentUpdate(BaseModel):
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
        name=student.identity.name,
        surname=student.identity.surname,
        email=student.identity.email,
        profile_photo_uri=student.identity.profile_photo_uri,
        birth_date=student.identity.date_of_birth,
        group=group,
        is_verified=student.identity.is_verified,
    )
