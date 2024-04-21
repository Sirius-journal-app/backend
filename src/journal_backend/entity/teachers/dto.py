from dataclasses import dataclass
from datetime import date
from typing import Optional

from fastapi_users import schemas
from pydantic import BaseModel, EmailStr, Field

from journal_backend.entity.teachers.models import Teacher


@dataclass(frozen=True, kw_only=True)
class TeacherRead:
    name: str
    surname: str
    profile_photo_uri: str = ""
    birth_date: Optional[date] = None
    qualification: str
    education: str
    email: str
    is_verified: bool


class TeacherCreate(BaseModel):
    name: str
    surname: str
    date_of_birth: Optional[date] = None
    email: EmailStr
    password: str
    qualification: str
    education: str
    competencies: list[str] = Field(default_factory=list)


class TeacherUpdate(schemas.BaseUserUpdate):
    pass


@dataclass(frozen=True, kw_only=True)
class AuthResponse:
    token: str
    teacher: TeacherRead


def model_to_read_dto(teacher: Teacher) -> TeacherRead:
    return TeacherRead(
        name=teacher.identity.name,
        surname=teacher.identity.surname,
        email=teacher.identity.email,
        profile_photo_uri=teacher.identity.profile_photo_uri,
        birth_date=teacher.identity.date_of_birth,
        qualification=teacher.qualification,
        education=teacher.education,
        is_verified=teacher.identity.is_verified,
    )
