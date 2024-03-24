from datetime import datetime
from typing import Optional

from fastapi_users import schemas


class TeacherRead(schemas.BaseUser[int]):
    email: str
    registered_at: datetime

class TeacherCreate(schemas.BaseUserCreate):
    username: Optional[str] = None


class TeacherUpdate(schemas.BaseUserUpdate):
    username: Optional[str]
