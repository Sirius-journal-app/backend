import fastapi_users.router
from fastapi import APIRouter, Depends
from fastapi_users.fastapi_users import (  # type: ignore[attr-defined]
    get_auth_router,
    get_register_router,
    get_users_router,
)

from journal_backend.entity.users.dependencies import current_user, get_user_service
from journal_backend.entity.users.models import UserIdentity

router = APIRouter(prefix="/students", tags=["students"])


@router.get("/{student_id}")
async def retrieve_student(student_id: int, caller: UserIdentity = Depends(current_user)):
    return caller.role


@router.get("/{student_id}/academic_reports")
async def get_student_academic_reports(
        caller: UserIdentity = Depends(current_user),
):
    pass
