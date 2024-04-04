from datetime import date

from fastapi_users import schemas
from pydantic import BaseModel


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
    email: str
    password: str
    qualification: str
    education: str
    competencies: list[str]


class TeacherUpdate(schemas.BaseUserUpdate):
    pass
