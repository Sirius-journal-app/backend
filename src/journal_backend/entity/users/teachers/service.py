from typing import Optional

from fastapi import Request
from fastapi_users import BaseUserManager, IntegerIDMixin
from fastapi_users.password import PasswordHelperProtocol

from journal_backend.entity.users.teachers.models import Teacher
from journal_backend.entity.users.teachers.repository import TeacherRepository


class TeacherService(IntegerIDMixin, BaseUserManager[Teacher, int]):
    def __init__(
        self,
        teacher_repo: TeacherRepository,
        token_secret: str,
        password_helper: Optional[PasswordHelperProtocol] = None,
    ) -> None:
        self.reset_password_token_secret = token_secret
        self.verification_token_secret = token_secret

        super().__init__(teacher_repo, password_helper)

    async def on_after_register(
        self, teacher: Teacher, request: Optional[Request] = None
    ) -> None:
        print(f"Teacher {teacher.id} has registered.")

    async def on_after_forgot_password(
        self, teacher: Teacher, token: str, request: Optional[Request] = None
    ) -> None:
        print(f"Teacher {teacher.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, teacher: Teacher, token: str, request: Optional[Request] = None
    ) -> None:
        print(f"Verification requested for teacher {teacher.id}. Verification token: {token}")
