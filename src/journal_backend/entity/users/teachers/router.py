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
from journal_backend.entity.users.teachers.dependencies import get_teacher_service
from journal_backend.entity.users.teachers.models import Teacher
from journal_backend.entity.users.teachers.schemas import TeacherCreate, TeacherRead, TeacherUpdate

router = APIRouter(prefix="/teachers")


def get_jwt_strategy(config: Config = Depends(Stub(Config))) -> JWTStrategy[Teacher, int]:
    return JWTStrategy(secret=config.app.jwt_secret, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=BearerTransport(tokenUrl="teachers/login"),
    get_strategy=get_jwt_strategy,
)
authenticator = Authenticator(
    backends=[auth_backend], get_user_manager=get_teacher_service
)

router.include_router(
    get_users_router(get_teacher_service, TeacherRead, TeacherUpdate, authenticator),
    tags=["teachers"],
)

router.include_router(
    get_auth_router(
        auth_backend,
        get_teacher_service,
        authenticator,
    ),
    prefix="/auth/jwt",
    tags=["teachers"],
)

router.include_router(
    get_register_router(get_teacher_service, TeacherRead, TeacherCreate),
    prefix="/auth",
    tags=["teachers"],
)

router.include_router(
    get_reset_password_router(get_teacher_service),
    prefix="/auth",
    tags=["teachers"],
)

router.include_router(
    get_verify_router(get_teacher_service, TeacherRead),
    prefix="/auth",
    tags=["teachers"],
)
