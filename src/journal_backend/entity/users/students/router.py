from fastapi import APIRouter, Depends
from fastapi_users.authentication import (
    AuthenticationBackend,
    Authenticator,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.fastapi_users import (  # type: ignore[attr-defined]
    get_auth_router,
    get_register_router,
    get_users_router,
)
from fastapi_users.router import get_reset_password_router, get_verify_router

from journal_backend.config import Config
from journal_backend.depends_stub import Stub
from journal_backend.entity.users.students.dependencies import get_student_service
from journal_backend.entity.users.students.models import Student
from journal_backend.entity.users.students.schemas import StudentCreate, StudentRead, StudentUpdate

router = APIRouter(prefix="/students")


def get_jwt_strategy(config: Config = Depends(Stub(Config))) -> JWTStrategy[Student, int]:
    return JWTStrategy(secret=config.app.jwt_secret, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=BearerTransport(tokenUrl="students/login"),
    get_strategy=get_jwt_strategy,
)
authenticator = Authenticator(
    backends=[auth_backend], get_user_manager=get_student_service
)

router.include_router(
    get_users_router(get_student_service, StudentRead, StudentUpdate, authenticator),
    tags=["students"],
)

router.include_router(
    get_auth_router(
        auth_backend,
        get_student_service,
        authenticator,
    ),
    tags=["students"],
)

router.include_router(
    get_register_router(get_student_service, StudentRead, StudentCreate),
    tags=["students"],
)

router.include_router(
    get_reset_password_router(get_student_service),
    tags=["students"],
)

router.include_router(
    get_verify_router(get_student_service, StudentRead),
    tags=["students"],
)
