from passlib.context import CryptContext

from journal_backend.entity.teachers.dto import TeacherCreate
from journal_backend.entity.teachers.models import Teacher, Competence, Subject
from journal_backend.entity.teachers.repository import TeacherRepository
from journal_backend.entity.users import exceptions
from journal_backend.entity.users.enums import Role
from journal_backend.entity.users.repository import UserRepository


def hash_string(string: str) -> str:
    return str(hash(string))  # temp stub


class TeacherService:
    def __init__(
            self,
            repo: TeacherRepository,
            user_repo: UserRepository,
    ) -> None:
        self.repo = repo
        self.user_repo = user_repo
        self.context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def create(self, teacher_create: TeacherCreate) -> Teacher:
        existing = await self.user_repo.get_by_email(email=teacher_create.email)
        if existing:
            raise exceptions.UserAlreadyExists

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
        return new_teacher
