from datetime import date, timedelta
from typing import Literal, TypeAlias

from fastapi_users import jwt
from passlib.context import CryptContext

from journal_backend.config import AppConfig
from journal_backend.entity.academic_reports.models import AcademicReport
from journal_backend.entity.classes.models import Class
from journal_backend.entity.classes.repository import ClassRepository
from journal_backend.entity.students import exceptions
from journal_backend.entity.students.dto import StudentCreate
from journal_backend.entity.students.models import Student
from journal_backend.entity.students.repository import StudentRepository
from journal_backend.entity.users import exceptions as u_exceptions
from journal_backend.entity.users.enums import Role
from journal_backend.entity.users.models import UserIdentity
from journal_backend.entity.users.repository import UserRepository

DaySchedule: TypeAlias = list[Class]


class StudentService:
    def __init__(
            self,
            repo: StudentRepository,
            user_repo: UserRepository,
            class_repo: ClassRepository,
    ) -> None:
        self.repo = repo
        self.user_repo = user_repo
        self.class_repo = class_repo
        self.context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def create(
            self,
            student_create: StudentCreate,
            app_cfg: AppConfig
    ) -> tuple[str, Student]:
        existing = await self.user_repo.get_by_email(email=student_create.email)
        if existing:
            raise u_exceptions.UserAlreadyExists

        group = None
        if student_create.group_name:
            group = await self.repo.get_group_by_name(student_create.group_name)
            if not group:
                raise exceptions.GroupNotFound

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

        new_student = await self.repo.create(
            id=identity.id,
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

    async def get_schedule_by_id(
            self,
            student_id: int | Literal["me"],
            offset: int,
            caller: UserIdentity
    ) -> list[DaySchedule]:
        if student_id == "me":
            student_id = caller.id

        if caller.role == Role.STUDENT and caller.id != student_id:
            raise exceptions.StudentPermissionError

        student = await self.repo.get_by_id(student_id)
        if not student:
            raise exceptions.StudentNotFound

        now_with_offset = date.today() + timedelta(days=7 * offset)
        monday = now_with_offset - timedelta(days=now_with_offset.weekday())
        sunday = monday + timedelta(days=7)

        classes_on_a_week: list[Class] = await self.class_repo.get_schedule_by_group_id(
            student.group_id,
            monday,
            sunday
        )
        return self._aggregate_classes(classes_on_a_week)

    async def get_academic_reports_by_id(
            self,
            student_id: int | Literal["me"],
            offset: int,
            caller: UserIdentity
    ) -> list[AcademicReport]:
        if student_id == "me":
            student_id = caller.id

        if caller.role == Role.STUDENT and caller.id != student_id:
            raise exceptions.StudentPermissionError

        student: Student = await self.repo.get_by_id(student_id)
        if not student:
            raise exceptions.StudentNotFound

        now_with_offset = date.today() + timedelta(days=7 * offset)
        monday = now_with_offset - timedelta(days=now_with_offset.weekday())
        sunday = monday + timedelta(days=7)

        reports: list[AcademicReport] = await self.repo.get_academic_reports_by_id(
            student_id=student_id,
            d_left=monday,
            d_right=sunday,
        )

        return reports

    @staticmethod
    def _aggregate_classes(classes: list[Class]) -> list[DaySchedule]:
        schedule_by_days: dict[int, Class] = {}
        for class_ in classes:
            weekday = class_.starts_at.weekday()
            if not schedule_by_days.get(weekday):
                schedule_by_days[weekday] = []
            schedule_by_days[weekday].append(class_)
        return list(schedule_by_days.values())
