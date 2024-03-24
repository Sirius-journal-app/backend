from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from journal_backend.config import Config
from journal_backend.depends_stub import Stub
from journal_backend.entity.users.students.models import Student
from journal_backend.entity.users.students.repository import StudentRepository
from journal_backend.entity.users.students.service import StudentService


async def get_student_repository(
    session: AsyncSession = Depends(Stub(AsyncSession)),
) -> StudentRepository:
    yield StudentRepository(session, Student)


async def get_student_service(
    student_repository: StudentRepository = Depends(Stub(StudentRepository)),
    config: Config = Depends(Stub(Config)),
) -> StudentService:
    yield StudentService(student_repository, config.app.jwt_secret)
