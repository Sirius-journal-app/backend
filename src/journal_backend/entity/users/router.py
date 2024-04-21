from fastapi import APIRouter
from fastapi_users.fastapi_users import (  # type: ignore[attr-defined]
    get_auth_router,
    get_users_router,
)
from fastapi_users.router import get_reset_password_router, get_verify_router

from journal_backend.entity.users.dependencies import (
    auth_backend,
    authenticator,
    get_user_service,
)
from journal_backend.entity.users.dto import UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

router.include_router(
    get_users_router(get_user_service, UserRead, UserUpdate, authenticator),
    tags=["users"],
)

router.include_router(
    get_auth_router(
        auth_backend,
        get_user_service,
        authenticator,
    ),
    tags=["users"],
)


router.include_router(
    get_reset_password_router(get_user_service),
    tags=["users"],
)

router.include_router(
    get_verify_router(get_user_service, UserRead),
    tags=["users"],
)
