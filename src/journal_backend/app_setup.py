"""Contain functions required for configuration of the project components."""
from functools import partial
from typing import TYPE_CHECKING, TypeAlias

import uvicorn
from fastapi import APIRouter, FastAPI
from pydantic import BaseModel
from redis.asyncio import ConnectionPool, Redis, Connection
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin.contrib.sqla import Admin, ModelView

from journal_backend.admin.auth_provider import MyAuthProvider
from journal_backend.admin.views import (
    ClassroomView,
    ClassView,
    SubjectView,
    TeacherView,
    UserIdentityView,
)
from journal_backend.config import AppConfig, Config, HttpServerConfig
from journal_backend.database.dependencies import get_session
from journal_backend.database.sa_utils import (
    create_engine,
    create_session_maker,
)
from journal_backend.depends_stub import Stub
from journal_backend.entity.classes.dependencies import get_class_repository
from journal_backend.entity.classes.models import Class, Classroom
from journal_backend.entity.classes.repository import ClassRepository
from journal_backend.entity.common.dependencies import (
    get_email_sender,
    get_redis_conn,
)
from journal_backend.entity.common.email_sender import EmailSender
from journal_backend.entity.students.dependencies import (
    get_student_repository,
    get_student_service,
)
from journal_backend.entity.students.models import (
    AcademicReport,
    Group,
    Student,
)
from journal_backend.entity.students.repository import StudentRepository
from journal_backend.entity.students.router import groups_router
from journal_backend.entity.students.router import router as students_router
from journal_backend.entity.students.service import StudentService
from journal_backend.entity.teachers.dependencies import (
    get_teacher_repository,
    get_teacher_service,
)
from journal_backend.entity.teachers.models import Competence, Subject, Teacher
from journal_backend.entity.teachers.repository import TeacherRepository
from journal_backend.entity.teachers.router import router as teachers_router
from journal_backend.entity.teachers.service import TeacherService
from journal_backend.entity.users.dependencies import (
    get_user_repository,
    get_user_service,
)
from journal_backend.entity.users.models import UserIdentity
from journal_backend.entity.users.repository import UserRepository
from journal_backend.entity.users.router import router as users_router
from journal_backend.entity.users.service import UserService

router = APIRouter()

if TYPE_CHECKING:
    ConnectionPoolT: TypeAlias = ConnectionPool[Connection]
else:
    ConnectionPoolT = ConnectionPool


class MsgResponse(BaseModel):
    """Represent a simple string message response.

    Attributes:
        msg (str): The message itself.
    """

    msg: str


@router.get("/")
async def read_main() -> MsgResponse:
    """Read the root endpoint (Only in testing purposes).

    Returns:
        MsgResponse: The message response instance.
    """
    return MsgResponse(msg="Welcome to Sirius-journal API!")


def initialise_routers(app: FastAPI) -> None:
    """Include all routers to the app.

    Args:
        app (FastAPI): The FastAPI instance.
    """
    app.include_router(router)
    app.include_router(users_router)
    app.include_router(teachers_router)
    app.include_router(students_router)
    app.include_router(groups_router)


def initialise_dependencies(
        app: FastAPI,
        config: Config,
        redis_pool: ConnectionPoolT
) -> None:
    """Initialise the dependencies in the app.

    Args:
        app (FastAPI): The FastAPI instance.
        config (Config): The config instance.
        redis_pool (ConnectionPoolT): The redis connection pool.
    """
    engine = create_engine(config.db.uri)
    session_factory = create_session_maker(engine)

    admin = Admin(
        engine,
        title="Sirius Journal admin",
        auth_provider=MyAuthProvider(
            session_factory,
        ),
        middlewares=[Middleware(SessionMiddleware, secret_key=config.app.jwt_secret)],
    )
    admin.add_view(UserIdentityView(UserIdentity))
    admin.add_view(ModelView(Student))
    admin.add_view(ModelView(Group))
    admin.add_view(TeacherView(Teacher))
    admin.add_view(SubjectView(Subject))
    admin.add_view(ClassroomView(Classroom))
    admin.add_view(ModelView(Competence))
    admin.add_view(ClassView(Class, label='Classes'))
    admin.add_view(ModelView(AcademicReport))
    admin.mount_to(app)

    app.dependency_overrides[Stub(AsyncSession)] = partial(get_session, session_factory)
    app.dependency_overrides[Stub(Config)] = lambda: config
    app.dependency_overrides[Stub(AppConfig)] = lambda: config.app

    app.dependency_overrides[Stub(EmailSender)] = get_email_sender
    app.dependency_overrides[Stub(Redis)] = partial(get_redis_conn, redis_pool)
    app.dependency_overrides[Stub(UserRepository)] = get_user_repository
    app.dependency_overrides[Stub(UserService)] = get_user_service
    app.dependency_overrides[Stub(StudentRepository)] = get_student_repository
    app.dependency_overrides[Stub(ClassRepository)] = get_class_repository
    app.dependency_overrides[Stub(StudentService)] = get_student_service
    app.dependency_overrides[Stub(TeacherRepository)] = get_teacher_repository
    app.dependency_overrides[Stub(TeacherService)] = get_teacher_service


def create_app(app_cfg: AppConfig) -> FastAPI:
    """Create a FastAPI instance.

    Args:
        app_cfg (AppConfig): The app configuration.

    Returns:
        FastAPI: The created FastAPI instance.
    """
    app = FastAPI(
        title=app_cfg.title,
        description=app_cfg.description,
        version=app_cfg.version,
    )
    return app


def create_http_server(
        app: FastAPI, http_server_cfg: HttpServerConfig
) -> uvicorn.Server:
    """Create uvicorn HTTP server instance.

    Args:
        app (FastAPI): The FastAPI instance.
        http_server_cfg (HttpServerConfig): The HTTP server configuration.

    Returns:
        uvicorn.Server: The created Uvicorn server instance.
    """
    uvicorn_config = uvicorn.Config(
        app,
        host=http_server_cfg.host,
        port=http_server_cfg.port,
        log_level=http_server_cfg.log_level,
    )
    return uvicorn.Server(uvicorn_config)
