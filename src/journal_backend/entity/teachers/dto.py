from dataclasses import field, dataclass
from datetime import date

from fastapi_users import schemas
from pydantic import BaseModel, Field, EmailStr


@dataclass(frozen=True, kw_only=True)
class TeacherRead:
    name: str
    surname: str
    profile_photo_uri: str
    birth_date: date
    qualification: str
    education: str
    email: str
    is_verified: bool


class TeacherCreate(BaseModel):
    name: str
    surname: str
    date_of_birth: date
    email: EmailStr
    password: str
    qualification: str
    education: str
    competencies: list[str] = Field(default_factory=list)


class TeacherUpdate(schemas.BaseUserUpdate):
    pass
