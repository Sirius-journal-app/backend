from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from journal_backend.entity.teachers.models import Subject, Teacher


class TeacherRepository:
    def __init__(
            self,
            session: AsyncSession,
    ) -> None:
        self.session = session

    async def create(self, **creds: Any) -> Teacher:
        teacher = Teacher(**creds)
        self.session.add(teacher)
        await self.session.commit()
        await self.session.refresh(teacher)
        return teacher

    async def get_subject_by_name(self, name: str) -> Subject:
        stmt = select(Subject).where(Subject.name == name)
        subject = await self.session.scalar(stmt)
        if not subject:
            return Subject(name=name)
        return subject

    async def get_by_id(self, teacher_id: int) -> Teacher:
        stmt = select(Teacher).where(Teacher.id == teacher_id)
        teacher = await self.session.scalar(stmt)
        return teacher
