from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, Any

from fastapi_users.schemas import CreateUpdateDictModel
from pydantic import BaseModel, EmailStr, Field

from journal_backend.entity.students.models import Student


@dataclass(frozen=True, kw_only=True)
class StudentRead:
    name: str
    surname: str
    email: str
    profile_photo_uri: str
    birth_date: Optional[datetime] = None
    admission_year: Optional[int] = None
    group: Optional[str] = None
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
    return StudentRead(
        name=student.identity.name,
        surname=student.identity.surname,
        email=student.identity.email,
        profile_photo_uri=student.identity.profile_photo_uri,
        birth_date=student.identity.date_of_birth,
        admission_year=student.admission_year,
        group=student.group,
        is_verified=student.identity.is_verified,
    )
