from typing import AsyncGenerator

from sqlalchemy.orm import Session, sessionmaker

from journal_backend.database.sa_utils import create_session


async def get_session(
    session_factory: sessionmaker[Session],
) -> AsyncGenerator[Session, None]:
    async with create_session(session_factory) as session:
        yield session