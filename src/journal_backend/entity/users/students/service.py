from typing import Optional, List

from fastapi import Request
from fastapi_users import BaseUserManager, IntegerIDMixin
from fastapi_users.password import PasswordHelperProtocol

from journal_backend.entity.academic_reports.models import AcademicReport
from journal_backend.entity.users.students.models import Student
from journal_backend.entity.users.students.repository import StudentRepository


class StudentService(IntegerIDMixin, BaseUserManager[Student, int]):
    def __init__(
            self,
            student_repo: StudentRepository,
            token_secret: str,
            password_helper: Optional[PasswordHelperProtocol] = None,
    ) -> None:
        self.reset_password_token_secret = token_secret
        self.verification_token_secret = token_secret

        super().__init__(student_repo, password_helper)

    async def on_after_register(
            self, student: Student, request: Optional[Request] = None
    ) -> None:
        print(f"Student {student.id} has registered.")

    async def on_after_forgot_password(
            self, student: Student, token: str, request: Optional[Request] = None
    ) -> None:
        print(f"Student {student.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
            self, student: Student, token: str, request: Optional[Request] = None
    ) -> None:
        print(f"Verification requested for student {student.id}. Verification token: {token}")
