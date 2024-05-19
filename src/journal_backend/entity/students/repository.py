from datetime import date
from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from journal_backend.entity.academic_reports.models import AcademicReport
from journal_backend.entity.classes.models import Class
from journal_backend.entity.students.models import Group, Student


class StudentRepository:
    def __init__(
            self,
            session: AsyncSession,
    ) -> None:
        self.session = session

    async def create(self, **creds: Any) -> Student:
        student = Student(**creds)
        self.session.add(student)
        await self.session.commit()
        await self.session.refresh(student)
        return student

    async def get_by_id(self, student_id: int) -> Student:
        stmt = select(Student).where(Student.id == student_id)
        student = await self.session.scalar(stmt)
        return student

    async def get_group_by_name(self, name: str) -> Group:
        stmt = select(Group).where(Group.name == name)
        group = await self.session.scalar(stmt)
        return group

    async def get_academic_reports_by_id(
            self,
            student_id: int,
            d_left: date,
            d_right: date
    ) -> Sequence[AcademicReport]:
        stmt = (
            select(AcademicReport).
            join(Class, onclause=Class.id == AcademicReport.lesson_id).
            where(AcademicReport.student_id == student_id).
            where(Class.starts_at.between(d_left, d_right))
        )

        res = await self.session.scalars(stmt)
        return res.unique().all()
