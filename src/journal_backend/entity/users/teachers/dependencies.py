from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from journal_backend.config import Config
from journal_backend.depends_stub import Stub
from journal_backend.entity.users.teachers.models import Teacher
from journal_backend.entity.users.teachers.repository import TeacherRepository
from journal_backend.entity.users.teachers.service import TeacherService


async def get_teacher_repository(
    session: AsyncSession = Depends(Stub(AsyncSession)),
) -> TeacherRepository:
    yield TeacherRepository(session, Teacher)


async def get_teacher_service(
    teacher_repository: TeacherRepository = Depends(Stub(TeacherRepository)),
    config: Config = Depends(Stub(Config)),
) -> TeacherService:
    yield TeacherService(teacher_repository, config.app.jwt_secret)
