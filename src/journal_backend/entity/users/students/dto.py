from datetime import datetime
from typing import Optional, Any

from fastapi_users import schemas
from fastapi_users.schemas import CreateUpdateDictModel


class StudentRead(schemas.BaseUser[int]):
    email: str


class StudentCreate(schemas.BaseUserCreate):
    name: str
    surname: str
    admission_year: int = 1


class StudentUpdate(CreateUpdateDictModel):
    param: str
    value: Any
