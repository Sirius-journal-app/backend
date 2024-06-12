from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from journal_backend.config import Config
from journal_backend.depends_stub import Stub
from journal_backend.entity.classes.dto import (
    DailySchedule,
    build_schedule_response,
)
from journal_backend.entity.classes.exceptions import ClassNotFound
from journal_backend.entity.common.pagination import (
    PaginationResponse,
    generate_pagination_response,
)
from journal_backend.entity.students import exceptions
from journal_backend.entity.students.dto import (
    AcademicReportCreate,
    AcademicReportRead,
    AuthResponse,
    Group,
    StudentCreate,
    StudentRead,
    build_academic_reports_response,
    model_to_read_dto,
)
from journal_backend.entity.students.service import StudentService
from journal_backend.entity.users import exceptions as u_exceptions
from journal_backend.entity.users.dependencies import current_user
from journal_backend.entity.users.models import UserIdentity

router = APIRouter(prefix="/students", tags=["students"])
groups_router = APIRouter(prefix="/groups", tags=["students", "groups"])


@router.post("")
async def register(
        student_body: StudentCreate,
        student_service: StudentService = Depends(Stub(StudentService)),
        cfg: Config = Depends(Stub(Config)),
) -> AuthResponse:
    try:
        auth_token, student = await student_service.create(
            student_create=student_body,
            app_cfg=cfg.app,
            smtp_cfg=cfg.smtp,
        )
    except u_exceptions.UserAlreadyExists as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except exceptions.GroupNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    return AuthResponse(
        token=auth_token,
        student=model_to_read_dto(student)
    )


@router.get("/{student_id}")
async def retrieve_student(
        student_id: int | Literal["me"],
        caller: UserIdentity = Depends(current_user),
        student_service: StudentService = Depends(Stub(StudentService))
) -> StudentRead:
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

    return model_to_read_dto(student)


@router.get("/{student_id}/schedule")
async def get_student_weekly_schedule(
        student_id: int | Literal["me"],
        offset: int = 0,
        caller: UserIdentity = Depends(current_user),
        student_service: StudentService = Depends(Stub(StudentService))
) -> PaginationResponse[DailySchedule]:
    try:
        classes_by_days = await student_service.get_schedule_by_id(student_id, offset, caller)
    except exceptions.StudentNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    uri_prefix = f"{router.prefix}/{student_id}/schedule"
    return PaginationResponse(
        next_url=f"{uri_prefix}?offset={offset + 1}",
        prev_url=f"{uri_prefix}?offset={offset - 1}",
        data=build_schedule_response(classes_by_days),
    )


@router.get("/{student_id}/academic_reports")
async def get_student_academic_reports(
        student_id: int | Literal["me"],
        offset: int = 0,
        caller: UserIdentity = Depends(current_user),
        student_service: StudentService = Depends(Stub(StudentService))
) -> PaginationResponse[AcademicReportRead]:
    try:
        reports = await student_service.get_academic_reports_by_id(student_id, offset, caller)
    except exceptions.StudentNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    uri_prefix = f"{router.prefix}/{student_id}/academic_reports"
    return PaginationResponse(
        next_url=f"{uri_prefix}?offset={offset + 1}",
        prev_url=f"{uri_prefix}?offset={offset - 1}",
        data=build_academic_reports_response(reports),
    )


@router.post('/academic_reports')
async def create_academic_reports(
        reports: list[AcademicReportCreate],
        caller: UserIdentity = Depends(current_user),
        service: StudentService = Depends(Stub(StudentService))
) -> None:
    try:
        await service.create_academic_reports(reports, caller)
    except exceptions.StudentPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except ClassNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@groups_router.get('/{group_id}')
async def retrieve_group_info(
        group_id: int,
        service: StudentService = Depends(Stub(StudentService)),
) -> Group:
    group = await service.get_group_info_by_id(group_id)
    return Group(
        id=group.id,
        name=group.name,
        admission_year=group.admission_year,
    )


@groups_router.get('/{group_id}/students')
async def get_group_students(
        group_id: int,
        limit: int = 25,
        offset: int = 0,
        caller: UserIdentity = Depends(current_user),
        service: StudentService = Depends(Stub(StudentService)),
) -> PaginationResponse[StudentRead]:
    try:
        students, total_in_group = await service.get_students_by_group_id(
            group_id,
            caller,
            limit,
            offset
        )
    except exceptions.StudentPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except exceptions.GroupNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return generate_pagination_response(
        uri_prefix=f"{groups_router.prefix}/{group_id}",
        offset=offset,
        limit=limit,
        max_offset=total_in_group,
        data=[
            model_to_read_dto(student)
            for student in students
        ]
    )
