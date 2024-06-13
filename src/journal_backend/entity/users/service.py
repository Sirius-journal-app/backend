from typing import TYPE_CHECKING, Optional, TypeAlias

from fastapi import Request
from fastapi_users import BaseUserManager, IntegerIDMixin
from fastapi_users.password import PasswordHelperProtocol
from redis.asyncio import Redis

from journal_backend.entity.users import exceptions
from journal_backend.entity.users.models import UserIdentity
from journal_backend.entity.users.repository import UserRepository

if TYPE_CHECKING:
    RedisT: TypeAlias = Redis[str]  # type:ignore
else:
    RedisT = Redis


class UserService(IntegerIDMixin, BaseUserManager[UserIdentity, int]):
    def __init__(
            self,
            user_repo: UserRepository,
            token_secret: str,
            redis_conn: RedisT,
            password_helper: Optional[PasswordHelperProtocol] = None,
    ) -> None:
        self.reset_password_token_secret = token_secret
        self.verification_token_secret = token_secret
        self.redis_conn = redis_conn

        super().__init__(user_repo, password_helper)

    async def confirm_email(self, token: str, caller: UserIdentity) -> None:
        student_id = await self.redis_conn.get(token)
        if not student_id:
            raise exceptions.InvalidConfirmationToken

        if int(student_id) != caller.id:
            raise exceptions.InvalidIdentity

        await self.user_db.set_verified(int(student_id))  # type:ignore[attr-defined]
        await self.redis_conn.delete(token)

    async def on_after_register(
            self, user: UserIdentity, request: Optional[Request] = None
    ) -> None:
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
            self, user: UserIdentity, token: str, request: Optional[Request] = None
    ) -> None:
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
            self, user: UserIdentity, token: str, request: Optional[Request] = None
    ) -> None:
        print(f"Verification requested for user {user.id}. Verification token: {token}")
