from unittest.mock import AsyncMock

from fastapi import FastAPI
from redis.asyncio import Redis
from starlette import status
from starlette.testclient import TestClient

from journal_backend.depends_stub import Stub
from journal_backend.entity.classes.repository import ClassRepository
from journal_backend.entity.common.email_sender import EmailSender
from journal_backend.entity.students.models import Student
from journal_backend.entity.students.repository import StudentRepository
from journal_backend.entity.teachers.models import Teacher
from journal_backend.entity.teachers.repository import TeacherRepository
from journal_backend.entity.users.enums import Role
from journal_backend.entity.users.models import UserIdentity
from journal_backend.entity.users.repository import UserRepository


def test_register_student(client: TestClient, app: FastAPI):
    student_repo_mock = AsyncMock()
    user_repo_mock = AsyncMock()
    class_repo_mock = AsyncMock()
    redis_conn_mock = AsyncMock()
    email_sender_mock = AsyncMock()
    app.dependency_overrides[Stub(StudentRepository)] = lambda: student_repo_mock
    app.dependency_overrides[Stub(UserRepository)] = lambda: user_repo_mock
    app.dependency_overrides[Stub(ClassRepository)] = lambda: class_repo_mock
    app.dependency_overrides[Stub(Redis)] = lambda: redis_conn_mock
    app.dependency_overrides[Stub(EmailSender)] = lambda: email_sender_mock

    user_repo_mock.get_by_email.return_value = None

    user = UserIdentity(
        id=1,
        name='a;gvas',
        surname='sglaglsa',
        email="gkagka@gmail.com",
        hashed_password='$2b$12$sxweSXb8uHr3SN30Q5hiGOLTiiQV4dMGq1X9SOwMOM.eztvmot.C.',
        role=Role.STUDENT,
        is_active=True,
        is_verified=False
    )
    user_repo_mock.create.return_value = user

    student_repo_mock.create.return_value = Student(
        id=1,
        group_id=1,
        identity=user,
    )

    resp = client.post("students", json={
        "id": user.id,
        "name": user.name,
        "surname": user.surname,
        "email": user.email,
        "password": '123',
        "group_name": 'fasf',
    })
    expected_status = status.HTTP_200_OK
    assert resp.status_code == expected_status


#
def test_register_teacher(client: TestClient, app: FastAPI):
    teacher_repo_mock = AsyncMock()
    user_repo_mock = AsyncMock()
    class_repo_mock = AsyncMock()
    redis_conn_mock = AsyncMock()
    email_sender_mock = AsyncMock()
    app.dependency_overrides[Stub(TeacherRepository)] = lambda: teacher_repo_mock
    app.dependency_overrides[Stub(UserRepository)] = lambda: user_repo_mock
    app.dependency_overrides[Stub(ClassRepository)] = lambda: class_repo_mock
    app.dependency_overrides[Stub(Redis)] = lambda: redis_conn_mock
    app.dependency_overrides[Stub(EmailSender)] = lambda: email_sender_mock

    user_repo_mock.get_by_email.return_value = None

    user = UserIdentity(
        id=1,
        name='a;gvas',
        surname='sglaglsa',
        email="gkagka@gmail.com",
        hashed_password='$2b$12$sxweSXb8uHr3SN30Q5hiGOLTiiQV4dMGq1X9SOwMOM.eztvmot.C.',
        role=Role.STUDENT,
        is_active=True,
        is_verified=False
    )
    user_repo_mock.create.return_value = user

    teacher_repo_mock.create.return_value = Teacher(
        id=1,
        qualification="blalblblabl",
        education='blalblblabl',
        identity=user,
    )

    resp = client.post("teachers", json={
        "id": user.id,
        "name": user.name,
        "surname": user.surname,
        "email": user.email,
        "password": '123',
        "qualification": 'blalblblabl',
        "education": 'blalblblabl'
    })
    expected_status = status.HTTP_200_OK
    assert resp.status_code == expected_status
