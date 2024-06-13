from fastapi import APIRouter, Depends, HTTPException
from fastapi_users.fastapi_users import (  # type: ignore[attr-defined]
    get_auth_router,
    get_users_router,
)
from fastapi_users.router import get_reset_password_router, get_verify_router
from starlette import status

from journal_backend.depends_stub import Stub
from journal_backend.entity.users import exceptions
from journal_backend.entity.users.dependencies import (
    auth_backend,
    authenticator,
    current_user,
    get_user_service,
)
from journal_backend.entity.users.dto import UserRead, UserUpdate
from journal_backend.entity.users.models import UserIdentity
from journal_backend.entity.users.service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get('/confirm-email')
async def confirm_email(
        em_token: str,
        caller: UserIdentity = Depends(current_user),
        user_service: UserService = Depends(Stub(UserService)),
) -> str:
    try:
        await user_service.confirm_email(em_token, caller)
    except exceptions.InvalidConfirmationToken as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except exceptions.InvalidIdentity as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    return "OK"


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
