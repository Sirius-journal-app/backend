from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    Authenticator,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.jwt import decode_jwt
from jwt import InvalidTokenError
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from journal_backend.config import Config
from journal_backend.depends_stub import Stub
from journal_backend.entity.users.models import UserIdentity
from journal_backend.entity.users.repository import UserRepository
from journal_backend.entity.users.service import UserService

JWT_ALGORITHM = "HS256"
JWT_AUDIENCE = "fastapi-users:auth"


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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


async def current_user(
        token: str = Depends(oauth2_scheme),
        cfg: Config = Depends(Stub(Config)),
        user_repo: UserRepository = Depends(Stub(UserRepository))
) -> UserIdentity:
    try:
        user_id = int(decode_jwt(
            encoded_jwt=token,
            secret=SecretStr(cfg.app.jwt_secret),
            audience=[JWT_AUDIENCE],
            algorithms=[JWT_ALGORITHM],
        )['sub'])
    except (InvalidTokenError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid auth token"
        )

    user = await user_repo.get(user_id)
    return user
