from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from journal_backend.app_setup import create_app, initialise_routers
from journal_backend.config import Config
from journal_backend.depends_stub import Stub
from journal_backend.entity.students.dependencies import get_student_service
from journal_backend.entity.students.service import StudentService
from journal_backend.entity.teachers.dependencies import get_teacher_service
from journal_backend.entity.teachers.service import TeacherService
from journal_backend.entity.users.dependencies import get_user_service
from journal_backend.entity.users.service import UserService


@pytest.fixture(scope="function")
def config_mock() -> Mock:
    return Mock()


@pytest.fixture(scope="function")
def robot_facade_mock() -> AsyncMock:
    return AsyncMock()


@pytest.fixture(scope="function")
def report_repo_mock() -> AsyncMock:
    return AsyncMock()


@pytest.fixture(scope="function")
def app(config_mock: Mock):
    return create_app(config_mock)


@pytest.fixture(scope="function", autouse=True)
def init_routers(app: FastAPI):
    initialise_routers(app)


@pytest.fixture(scope="function", autouse=True)
def init_basic_dependencies(
        app: FastAPI,
        config_mock: Mock,
        robot_facade_mock: Mock,
        report_repo_mock: Mock
):
    session_mock = AsyncMock()
    config_mock.app.jwt_lifetime_seconds = 5
    config_mock.app.jwt_secret = "secret"
    config_mock.smtp.email = "randomshit@gmail.com"

    app.dependency_overrides[Stub(UserService)] = get_user_service
    app.dependency_overrides[Stub(StudentService)] = get_student_service
    app.dependency_overrides[Stub(TeacherService)] = get_teacher_service
    app.dependency_overrides[Stub(AsyncSession)] = lambda: session_mock
    app.dependency_overrides[Stub(Config)] = lambda: config_mock


@pytest.fixture(scope="function")
def client(app: FastAPI) -> TestClient:
    return TestClient(app, headers={"Accept": "application/json"})
