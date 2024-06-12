import asyncio
import uuid
from datetime import date, timedelta
from email.message import EmailMessage
from typing import Literal, TypeAlias

from fastapi_users import jwt
from passlib.context import CryptContext
from redis.asyncio import Redis

from journal_backend.config import AppConfig, SMTPConfig
from journal_backend.entity.classes.exceptions import ClassNotFound
from journal_backend.entity.classes.models import Class
from journal_backend.entity.classes.repository import ClassRepository
from journal_backend.entity.common.email_sender import EmailSender
from journal_backend.entity.students import exceptions
from journal_backend.entity.students.dto import (
    AcademicReportCreate,
    StudentCreate,
)
from journal_backend.entity.students.models import AcademicReport, Student
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
            email_sender: EmailSender,
            redis_conn: Redis,
    ) -> None:
        self.repo = repo
        self.user_repo = user_repo
        self.class_repo = class_repo
        self.email_sender = email_sender
        self.redis_conn = redis_conn
        self.context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def create(
            self,
            student_create: StudentCreate,
            app_cfg: AppConfig,
            smtp_cfg: SMTPConfig,
    ) -> tuple[str, Student]:
        existing = await self.user_repo.get_by_email(email=student_create.email)
        if existing:
            raise u_exceptions.UserAlreadyExists

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

        one_time_token = uuid.uuid4()
        await self.redis_conn.setex(
            name=str(one_time_token),
            value=new_student.id,
            time=timedelta(minutes=10)
        )

        body = f"""
        Привет, перейди по ссылке ниже для подтверждения почты в течении 10 минут
        http://localhost:8000/students/confirm-email/?token={one_time_token}
        """
        em = EmailMessage()
        em['From'] = smtp_cfg.email
        em['To'] = student_create.email
        em['Subject'] = 'Mail confirmation'
        em.set_content(body)
        asyncio.create_task(self.email_sender.send_email(
            email_to=student_create.email,
            em=em,
            smtp_cfg=smtp_cfg
        ))

        await self.repo.session.commit()

        return auth_token, new_student

    async def confirm_email(self, token: str, caller: UserIdentity) -> None:
        student_id = await self.redis_conn.get(token)
        if not student_id:
            raise exceptions.InvalidConfirmationToken

        if int(student_id) != caller.id:
            raise exceptions.InvalidIdentity

        await self.user_repo.set_verified(int(student_id))
        await self.redis_conn.delete(token)

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
    ) -> dict[int, DaySchedule]:
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

    async def create_academic_reports(
            self,
            reports: list[AcademicReportCreate],
            caller: UserIdentity
    ) -> None:
        if caller.role == Role.STUDENT:
            raise exceptions.StudentPermissionError

        for report in reports:
            student = await self.repo.get_by_id(report.student_id)
            if not student:
                raise exceptions.StudentNotFound

            if not await self.class_repo.student_class_exists(student.group_id, report.class_id):
                raise ClassNotFound

        await self.repo.create_academic_reports(reports)

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

        reports: list[AcademicReport] = await self.repo.get_academic_reports(
            student_id=student_id,
            d_left=monday,
            d_right=sunday,
        )

        return reports

    async def get_students_by_group_id(
            self,
            group_id: int,
            caller: UserIdentity,
            limit: int,
            offset: int
    ) -> tuple[list[Student], int]:
        if caller.role == Role.STUDENT:
            raise exceptions.StudentPermissionError

        group = await self.repo.get_group_by_id(group_id)
        if not group:
            raise exceptions.GroupNotFound

        students, total_in_group = await self.repo.get_students_by_group_id(group_id, limit, offset)
        return students, total_in_group

    @staticmethod
    def _aggregate_classes(classes: list[Class]) -> dict[int, DaySchedule]:
        schedule_by_days: dict[int, Class] = {}
        for class_ in classes:
            weekday = class_.starts_at.weekday()
            if not schedule_by_days.get(weekday):
                schedule_by_days[weekday] = []
            schedule_by_days[weekday].append(class_)
        return schedule_by_days
