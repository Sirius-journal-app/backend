from fastapi_users import jwt
from passlib.context import CryptContext

from journal_backend.config import AppConfig
from journal_backend.entity.academic_reports.models import AcademicReport
from journal_backend.entity.students.dto import StudentCreate
from journal_backend.entity.students.models import Student
from journal_backend.entity.students.repository import StudentRepository
from journal_backend.entity.users import exceptions as u_exceptions
from journal_backend.entity.students import exceptions
from journal_backend.entity.users.enums import Role
from journal_backend.entity.users.models import UserIdentity
from journal_backend.entity.users.repository import UserRepository


class StudentService:
    def __init__(
            self,
            repo: StudentRepository,
            user_repo: UserRepository,
    ) -> None:
        self.repo = repo
        self.user_repo = user_repo
        self.context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def create(self, student_create: StudentCreate, app_cfg: AppConfig) -> (str, Student):
        existing = await self.user_repo.get_by_email(email=student_create.email)
        if existing:
            raise u_exceptions.UserAlreadyExists

        identity = await self.user_repo.create(
            {
                "name": student_create.name,
                "surname": student_create.surname,
                "email": student_create.email,
                "hashed_password": self.context.hash(student_create.password),
                "date_of_birth": student_create.date_of_birth,
                "role": Role.STUDENT,
                "is_verified": False,
            }
        )

        group = None
        if student_create.group_name:
            group = await self.repo.get_group_by_name(student_create.group_name)
            if not group:
                raise exceptions.GroupNotFound

        new_student = await self.repo.create(
            id=identity.id,
            admission_year=student_create.admission_year,
            group=group,
        )

        auth_token = jwt.generate_jwt(
            data={"sub": new_student.id},
            secret=app_cfg.jwt_secret,
            lifetime_seconds=app_cfg.jwt_lifetime_seconds
        )

        return auth_token, new_student

    async def get_by_id(self, student_id: int, caller: UserIdentity) -> Student:
        if caller.role == Role.STUDENT and caller.id != student_id:
            raise exceptions.StudentPermissionError

        student = await self.repo.get_by_id(student_id)
        if not student:
            raise exceptions.StudentNotFound

        return student

    async def get_academic_reports_by_id(self, student_id: int, caller: UserIdentity) -> list[AcademicReport]:
        if caller.role == Role.STUDENT and caller.id != student_id:
            raise exceptions.StudentPermissionError

        student: Student = await self.repo.get_by_id(student_id)
        if not student:
            raise exceptions.StudentNotFound

        if not student.academic_reports:
            student.academic_reports = []

        return student.academic_reports

