from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from journal_backend.entity.students.models import Student, Group


class StudentRepository:
    def __init__(
            self,
            session: AsyncSession,
    ) -> None:
        self.session = session

    async def create(self, **creds) -> Student:
        student = Student(**creds)
        self.session.add(student)
        await self.session.commit()
        await self.session.refresh(student)
        return student

    async def get_by_id(self, student_id) -> Student:
        stmt = select(Student).where(Student.id == student_id)
        student = await self.session.scalar(stmt)
        return student

    async def get_group_by_name(self, name: str) -> Group:
        stmt = select(Group).where(Group.name == name)
        group = await self.session.scalar(stmt)
        return group
