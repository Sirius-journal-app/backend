from datetime import date
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from journal_backend.entity.classes.models import Class


class ClassRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_schedule_by_group_id(
            self,
            group_id: int,
            d_left: date,
            d_right: date
    ) -> Sequence[Class]:
        stmt = (
            select(Class).
            where(Class.group_id == group_id).
            where(Class.starts_at.between(d_left, d_right))
        )

        res = await self.session.scalars(stmt)
        return res.unique().all()

    async def get_schedule_by_teacher_id(
            self,
            teacher_id: int,
            d_left: date,
            d_right: date
    ) -> Sequence[Class]:
        stmt = (
            select(Class).
            where(Class.teacher_id == teacher_id).
            where(Class.starts_at.between(d_left, d_right))
        )

        res = await self.session.scalars(stmt)
        return res.unique().all()

    async def student_class_exists(self, student_group_id: int, class_id: int) -> bool:
        stmt = (
            select(Class).
            where(Class.group_id == student_group_id).
            where(Class.id == class_id)
        )
        res = await self.session.execute(stmt)
        return bool(res.unique().scalar_one_or_none())
