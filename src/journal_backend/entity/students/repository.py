from datetime import date
from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from sqlalchemy.ext.asyncio import AsyncSession

from journal_backend.entity.classes.models import Class
from journal_backend.entity.students.dto import AcademicReportCreate
from journal_backend.entity.students.models import Group, Student, AcademicReport


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

    async def get_academic_reports(
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

    async def create_academic_reports(self, reports: list[AcademicReportCreate]):
        for report in reports:
            insert_stmt = (
                insert(AcademicReport).
                values(**report.__dict__).
                on_conflict_do_update(
                    index_elements=[AcademicReport.student_id, AcademicReport.class_id],
                    set_={'grade': report.grade, 'is_attended': report.is_attended}
                )
            )
            await self.session.execute(insert_stmt)
        await self.session.commit()
