from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, Any

from fastapi_users import schemas
from fastapi_users.schemas import CreateUpdateDictModel
from pydantic import BaseModel, Field, EmailStr


@dataclass(frozen=True, kw_only=True)
class StudentRead:
    name: str
    surname: str
    email: str
    profile_photo_uri: str
    birth_date: Optional[datetime]
    admission_year: Optional[int] = None
    group: Optional[str] = None
    is_verified: bool


class StudentCreate(BaseModel):
    name: str
    surname: str
    date_of_birth: date
    admission_year: int = 1
    email: EmailStr
    password: str
    group_name: Optional[str] = None


class StudentUpdate(CreateUpdateDictModel):
    param: str
    value: Any
