from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from fastapi_users.fastapi_users import (  # type: ignore[attr-defined]
    get_auth_router,
    get_register_router,
    get_users_router,
)
from starlette import status

from journal_backend.depends_stub import Stub
from journal_backend.entity.students import exceptions
from journal_backend.entity.users import exceptions as u_exceptions
from journal_backend.entity.students.dto import StudentRead, StudentCreate
from journal_backend.entity.students.service import StudentService
from journal_backend.entity.users.dependencies import current_user
from journal_backend.entity.users.models import UserIdentity

router = APIRouter(prefix="/students", tags=["students"])


@router.post("")
async def register(
        student_body: StudentCreate,
        student_service: StudentService = Depends(Stub(StudentService))
):
    try:
        student = await student_service.create(student_create=student_body)
    except u_exceptions.UserAlreadyExists as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return student.id


@router.get("/{student_id}")
async def retrieve_student(
        student_id: int  | Literal["me"],
        caller: UserIdentity = Depends(current_user),
        student_service: StudentService = Depends(Stub(StudentService))
):
    if student_id == "me":
        student_id = caller.id

    try:
        student = await student_service.get_by_id(student_id, caller)
    except exceptions.StudentNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except exceptions.StudentPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    return StudentRead(
        name=student.identity.name,
        surname=student.identity.surname,
        email=student.identity.email,
        profile_photo_uri=student.identity.profile_photo_uri,
        birth_date=student.identity.date_of_birth,
        admission_year=student.admission_year,
        group=student.group,
        is_verified=student.identity.is_verified,
    )


# @router.get("/{student_id}/academic_reports")
# async def get_student_academic_reports(
#         student_id: int,
#         caller: UserIdentity = Depends(current_user),
#         student_service: StudentService = Depends(Stub(StudentService))
# ):
#     try:
#         reports = await student_service.get_academic_reports_by_id(student_id, caller)
#     except exceptions.StudentNotFound as e:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=str(e)
#         )
#     return reports
