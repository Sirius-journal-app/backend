from typing import TYPE_CHECKING, TypeAlias

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from journal_backend.depends_stub import Stub
from journal_backend.entity.classes.repository import ClassRepository
from journal_backend.entity.common.email_sender import EmailSender
from journal_backend.entity.students.repository import StudentRepository
from journal_backend.entity.students.service import StudentService
from journal_backend.entity.users.repository import UserRepository

if TYPE_CHECKING:
    RedisT: TypeAlias = Redis[str]  # type:ignore
else:
    RedisT = Redis


async def get_student_repository(
        session: AsyncSession = Depends(Stub(AsyncSession)),
) -> StudentRepository:
    yield StudentRepository(session)


async def get_student_service(
        student_repository: StudentRepository = Depends(Stub(StudentRepository)),
        user_repository: UserRepository = Depends(Stub(UserRepository)),
        class_repository: ClassRepository = Depends(Stub(ClassRepository)),
        email_sender: EmailSender = Depends(Stub(EmailSender)),
        redis_conn: RedisT = Depends(Stub(Redis)),  # type:ignore
) -> StudentService:
    yield StudentService(
        student_repository,
        user_repository,
        class_repository,
        email_sender,
        redis_conn
    )
