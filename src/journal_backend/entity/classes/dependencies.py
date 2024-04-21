from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from journal_backend.depends_stub import Stub
from journal_backend.entity.classes.repository import ClassRepository


async def get_class_repository(
        session: AsyncSession = Depends(Stub(AsyncSession))
) -> ClassRepository:
    yield ClassRepository(session=session)
