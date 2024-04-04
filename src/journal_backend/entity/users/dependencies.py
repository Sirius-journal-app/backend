import fastapi_users
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import Authenticator, BearerTransport, AuthenticationBackend, JWTStrategy
from sqlalchemy.ext.asyncio import AsyncSession

from journal_backend.config import Config
from journal_backend.depends_stub import Stub
from journal_backend.entity.users.models import UserIdentity
from journal_backend.entity.users.repository import UserRepository
from journal_backend.entity.users.service import UserService


async def get_user_repository(
        session: AsyncSession = Depends(Stub(AsyncSession)),
) -> UserRepository:
    yield UserRepository(session, UserIdentity)


async def get_user_service(
        user_repository: UserRepository = Depends(Stub(UserRepository)),
        config: Config = Depends(Stub(Config)),
) -> UserService:
    yield UserService(user_repository, config.app.jwt_secret)


def get_jwt_strategy(config: Config = Depends(Stub(Config))) -> JWTStrategy[UserIdentity, int]:
    return JWTStrategy(secret=config.app.jwt_secret, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=BearerTransport(tokenUrl="users/login"),
    get_strategy=get_jwt_strategy,
)
authenticator = Authenticator(
    backends=[auth_backend], get_user_manager=get_user_service
)

fastapi_users_inst = FastAPIUsers(
    get_user_manager=get_user_service,
    auth_backends=[auth_backend]
)

ouath2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

# current_user = fastapi_users_inst.current_user(active=True)

def current_user(token: str = Depends(ouath2_scheme)):
    return token
