from fastapi_users import schemas


class TeacherRead(schemas.BaseUser[int]):
    email: str


class TeacherCreate(schemas.BaseUserCreate):
    name: str
    surname: str
    qualification: str
    education: str


class TeacherUpdate(schemas.BaseUserUpdate):
    pass
