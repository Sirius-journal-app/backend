from datetime import timedelta, date
from typing import TypeAlias, Literal

from fastapi_users import jwt
from passlib.context import CryptContext

from journal_backend.config import AppConfig
from journal_backend.entity.classes.models import Class
from journal_backend.entity.classes.repository import ClassRepository
from journal_backend.entity.teachers import exceptions
from journal_backend.entity.teachers.dto import TeacherCreate
from journal_backend.entity.teachers.models import Competence, Teacher
from journal_backend.entity.teachers.repository import TeacherRepository
from journal_backend.entity.users.enums import Role
from journal_backend.entity.users.exceptions import UserAlreadyExists
from journal_backend.entity.users.models import UserIdentity
from journal_backend.entity.users.repository import UserRepository

DaySchedule: TypeAlias = list[Class]


class TeacherService:
    def __init__(
            self,
            repo: TeacherRepository,
            user_repo: UserRepository,
            class_repo: ClassRepository,
    ) -> None:
        self.repo = repo
        self.user_repo = user_repo
        self.class_repo = class_repo
        self.context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def create(
            self,
            teacher_create: TeacherCreate,
            app_cfg: AppConfig
    ) -> tuple[str, Teacher]:
        existing = await self.user_repo.get_by_email(email=teacher_create.email)
        if existing:
            raise UserAlreadyExists

        identity = await self.user_repo.create(
            {
                "name": teacher_create.name,
                "surname": teacher_create.surname,
                "email": teacher_create.email,
                "hashed_password": self.context.hash(teacher_create.password),
                "date_of_birth": teacher_create.date_of_birth,
                "role": Role.TEACHER,
                "is_verified": False,
            }
        )

        new_teacher = await self.repo.create(
            id=identity.id,
            qualification=teacher_create.qualification,
            education=teacher_create.education,
            competencies=[
                Competence(
                    teacher_id=identity.id,
                    subject=await self.repo.get_subject_by_name(subject_name)
                )
                for subject_name in teacher_create.competencies
            ]
        )

        auth_token = jwt.generate_jwt(
            data={"sub": new_teacher.id},
            secret=app_cfg.jwt_secret,
            lifetime_seconds=app_cfg.jwt_lifetime_seconds
        )

        return auth_token, new_teacher

    async def get_by_id(self, teacher_id: int, caller: UserIdentity) -> Teacher:
        if caller.role != Role.ADMIN and teacher_id != caller.id:
            raise exceptions.TeacherPermissionError

        teacher = await self.repo.get_by_id(teacher_id)
        if not teacher:
            raise exceptions.TeacherNotFound

        return teacher

    async def get_competencies(self, teacher_id: int | Literal['me'], caller: UserIdentity) -> list[Competence]:
        if teacher_id == "me":
            teacher_id = caller.id

        if caller.role != Role.ADMIN and teacher_id != caller.id:
            raise exceptions.TeacherPermissionError

        teacher = await self.repo.get_by_id(teacher_id)
        if not teacher:
            raise exceptions.TeacherNotFound

        return teacher.competencies  # type:ignore[no-any-return]

    async def get_schedule_by_id(
            self,
            teacher_id: int | Literal["me"],
            offset: int,
            caller: UserIdentity
    ) -> list[DaySchedule]:
        if teacher_id == "me":
            teacher_id = caller.id

        if caller.role != Role.ADMIN and caller.id != teacher_id:
            raise exceptions.TeacherPermissionError

        teacher = await self.repo.get_by_id(teacher_id)
        if not teacher:
            raise exceptions.TeacherNotFound

        now_with_offset = date.today() + timedelta(days=7 * offset)
        monday = now_with_offset - timedelta(days=now_with_offset.weekday())
        sunday = monday + timedelta(days=7)

        classes_on_a_week: list[Class] = await self.class_repo.get_schedule_by_teacher_id(
            teacher_id,
            monday,
            sunday
        )
        return self._aggregate_classes(classes_on_a_week)

    @staticmethod
    def _aggregate_classes(classes: list[Class]) -> list[DaySchedule]:
        schedule_by_days: dict[int, Class] = {}
        for class_ in classes:
            weekday = class_.starts_at.weekday()
            if not schedule_by_days.get(weekday):
                schedule_by_days[weekday] = []
            schedule_by_days[weekday].append(class_)
        return schedule_by_days
