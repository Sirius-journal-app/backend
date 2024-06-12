from datetime import date
from typing import Any, Sequence

from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from journal_backend.entity.classes.models import Class
from journal_backend.entity.students.dto import AcademicReportCreate
from journal_backend.entity.students.models import (
    AcademicReport,
    Group,
    Student,
)


class StudentRepository:
    def __init__(
            self,
            session: AsyncSession,
    ) -> None:
        self.session = session

    async def create(self, **creds: Any) -> Student:
        student = Student(**creds)
        self.session.add(student)
        await self.session.flush()
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

    async def get_group_by_id(self, id_: int) -> Group:
        stmt = select(Group).where(Group.id == id_)
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
            join(Class, onclause=Class.id == AcademicReport.class_id).
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

    async def get_students_by_group_id(self, group_id: int, limit: int, offset: int) -> tuple[list[Student], int]:
        group_students_rows = (
            select(
                func.row_number().over(order_by=Student.id).label('id_in_group'),
                Student.id
            ).
            where(Student.group_id == group_id).cte()
        )
        stmt = (
            select(Student).
            add_cte(group_students_rows).
            join(group_students_rows, onclause=Student.id == group_students_rows.c.id).
            where(group_students_rows.c.id_in_group > offset).
            limit(limit)
        )
        res = await self.session.scalars(stmt)

        students = res.all()
        total_in_group = await self.session.scalar(
            select(func.count(group_students_rows.c.id)).add_cte(group_students_rows)
        )

        return students, total_in_group
