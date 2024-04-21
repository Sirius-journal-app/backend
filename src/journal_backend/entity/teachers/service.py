from fastapi_users import jwt
from passlib.context import CryptContext

from journal_backend.config import AppConfig
from journal_backend.entity.teachers import exceptions
from journal_backend.entity.teachers.dto import TeacherCreate
from journal_backend.entity.teachers.models import Competence, Teacher
from journal_backend.entity.teachers.repository import TeacherRepository
from journal_backend.entity.users.enums import Role
from journal_backend.entity.users.exceptions import UserAlreadyExists
from journal_backend.entity.users.models import UserIdentity
from journal_backend.entity.users.repository import UserRepository


class TeacherService:
    def __init__(
            self,
            repo: TeacherRepository,
            user_repo: UserRepository,
    ) -> None:
        self.repo = repo
        self.user_repo = user_repo
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

    async def get_competencies(self, teacher_id: int, caller: UserIdentity) -> list[Competence]:
        if caller.role != Role.ADMIN and teacher_id != caller.id:
            raise exceptions.TeacherPermissionError

        teacher = await self.repo.get_by_id(teacher_id)
        if not teacher:
            raise exceptions.TeacherNotFound

        return teacher.competencies  # type:ignore[no-any-return]
