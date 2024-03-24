# Функция для проверки токена
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordBearer
from journal_backend.config import Config, AppConfig
from journal_backend.depends_stub import Stub
from journal_backend.entity.users.students.dependencies import get_student_service
from journal_backend.entity.users.students.models import Student, Group
import jwt
from journal_backend.entity.users.students.repository import StudentRepository
from journal_backend.entity.users.students.service import StudentService
from sqlalchemy import select
from starlette import status


oauth2_students_scheme = OAuth2PasswordBearer(tokenUrl="students/login")


async def current_student(
        token: str = Depends(oauth2_students_scheme),
        student_repo: StudentRepository = Depends(Stub(StudentRepository)),
        app_cfg: AppConfig = Depends(Stub(AppConfig)),
) -> Student:
    try:
        payload = jwt.decode(token, app_cfg.jwt_secret, audience="fastapi-users:auth", algorithms=["HS256"])
    except (jwt.exceptions.DecodeError, jwt.exceptions.ExpiredSignatureError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    student_id = int(payload["sub"])
    student = await student_repo.get(student_id)

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student with provided credentials was not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return student
