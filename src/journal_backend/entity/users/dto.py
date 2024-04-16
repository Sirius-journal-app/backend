from datetime import date
from typing import Any

from fastapi_users import schemas
from fastapi_users.schemas import CreateUpdateDictModel

from journal_backend.entity.users.enums import Role


class UserRead(schemas.BaseUser[int]):
    email: str


class UserCreate(schemas.BaseUserCreate):
    name: str
    surname: str
    date_of_birth: date
    email: str
    password: str
    role: Role


class UserUpdate(CreateUpdateDictModel):
    param: str
    value: Any
