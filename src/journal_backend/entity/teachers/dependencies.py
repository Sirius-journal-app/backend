from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from journal_backend.depends_stub import Stub
from journal_backend.entity.classes.repository import ClassRepository
from journal_backend.entity.teachers.repository import TeacherRepository
from journal_backend.entity.teachers.service import TeacherService
from journal_backend.entity.users.repository import UserRepository


async def get_teacher_repository(
    session: AsyncSession = Depends(Stub(AsyncSession)),
) -> TeacherRepository:
    yield TeacherRepository(session)


async def get_teacher_service(
    teacher_repository: TeacherRepository = Depends(Stub(TeacherRepository)),
    user_repo: UserRepository = Depends(Stub(UserRepository)),
    class_repo: ClassRepository = Depends(Stub(ClassRepository)),
) -> TeacherService:
    yield TeacherService(teacher_repository, user_repo, class_repo)
