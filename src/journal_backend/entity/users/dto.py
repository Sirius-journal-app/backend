from typing import Any

from fastapi_users import schemas
from fastapi_users.schemas import CreateUpdateDictModel

from journal_backend.entity.users.enums import Role


class UserRead(schemas.BaseUser[int]):
    email: str


class UserCreate(schemas.BaseUserCreate):
    name: str
    surname: str
    role: Role


class UserUpdate(CreateUpdateDictModel):
    param: str
    value: Any
