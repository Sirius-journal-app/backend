from typing import Any, Dict, Optional, Type

from fastapi_users_db_sqlalchemy import (
    SQLAlchemyBaseOAuthAccountTable,
    SQLAlchemyUserDatabase,
)
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from journal_backend.entity.users.models import UserIdentity


class UserRepository(SQLAlchemyUserDatabase[UserIdentity, int]):
    def __init__(
            self,
            session: AsyncSession,
            user_table: Type[UserIdentity],
            oauth_account_table: Optional[
                Type[SQLAlchemyBaseOAuthAccountTable[int]]
            ] = None,
    ) -> None:
        super().__init__(session, user_table, oauth_account_table)

    async def create(self, create_dict: Dict[str, Any]) -> UserIdentity:
        user = self.user_table(**create_dict)
        self.session.add(user)
        await self.session.flush([user])
        await self.session.refresh(user)
        return user

    async def set_verified(self, student_id: int) -> None:
        stmt = update(UserIdentity).where(UserIdentity.id == student_id).values(is_verified=True)
        await self.session.execute(stmt)
        await self.session.commit()

    async def last(self) -> Optional[UserIdentity]:
        stmt = select(UserIdentity.id).order_by(UserIdentity.id.desc())
        last_id = await self.session.scalar(stmt)
        if last_id is None:
            return None
        return await self.get(last_id)
