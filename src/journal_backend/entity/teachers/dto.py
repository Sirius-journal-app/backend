from dataclasses import field
from datetime import date

from fastapi_users import schemas
from pydantic import BaseModel, Field, EmailStr


class TeacherRead(schemas.BaseUser[int]):
    email: str
    name: str
    surname: str
    qualification: str
    education: str


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
