from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from journal_backend.config import Config
from journal_backend.depends_stub import Stub
from journal_backend.entity.students.repository import StudentRepository
from journal_backend.entity.students.service import StudentService


async def get_student_repository(
    session: AsyncSession = Depends(Stub(AsyncSession)),
) -> StudentRepository:
    yield StudentRepository(session)


async def get_student_service(
    student_repository: StudentRepository = Depends(Stub(StudentRepository)),
) -> StudentService:
    yield StudentService(student_repository)
