from sqlalchemy.ext.asyncio import AsyncSession


class StudentRepository:
    def __init__(
            self,
            session: AsyncSession,
    ) -> None:
        self.session = session
