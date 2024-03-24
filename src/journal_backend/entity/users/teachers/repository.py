from typing import Optional, Type

from fastapi_users_db_sqlalchemy import (
    SQLAlchemyBaseOAuthAccountTable,
    SQLAlchemyUserDatabase,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from journal_backend.entity.users.teachers.models import Teacher


class TeacherRepository(SQLAlchemyUserDatabase[Teacher, int]):
    def __init__(
        self,
        session: AsyncSession,
        teacher_table: Type[Teacher],
        oauth_account_table: Optional[
            Type[SQLAlchemyBaseOAuthAccountTable[int]]
        ] = None,
    ) -> None:
        super().__init__(session, teacher_table, oauth_account_table)

    async def last(self) -> Optional[Teacher]:
        stmt = select(Teacher.id).order_by(Teacher.id.desc())
        last_id = await self.session.scalar(stmt)
        if last_id is None:
            return None
        return await self.get(last_id)
