from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from journal_backend.config import Config
from journal_backend.depends_stub import Stub
from journal_backend.entity.classes.dto import build_schedule_response
from journal_backend.entity.common.pagination import (
    PaginationResponse,
    generate_pagination_response,
)
from journal_backend.entity.teachers import exceptions
from journal_backend.entity.teachers.dto import (
    AuthResponse,
    TeacherCreate,
    TeacherRead,
    model_to_read_dto, TeacherCompetence,
)
from journal_backend.entity.teachers.models import Competence
from journal_backend.entity.teachers.service import TeacherService
from journal_backend.entity.users import exceptions as u_exceptions
from journal_backend.entity.users.dependencies import current_user
from journal_backend.entity.users.models import UserIdentity

router = APIRouter(prefix="/teachers", tags=['teachers'])


@router.post("")
async def register(
        teacher_body: TeacherCreate,
        teacher_service: TeacherService = Depends(Stub(TeacherService)),
        cfg: Config = Depends(Stub(Config)),
) -> AuthResponse:
    try:
        auth_token, teacher = await teacher_service.create(
            teacher_create=teacher_body,
            app_cfg=cfg.app
        )
    except u_exceptions.UserAlreadyExists as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return AuthResponse(
        token=auth_token,
        teacher=model_to_read_dto(teacher)
    )


@router.get("/{teacher_id}")
async def retrieve_teacher(
        teacher_id: int | Literal["me"],
        caller: UserIdentity = Depends(current_user),
        teacher_service: TeacherService = Depends(Stub(TeacherService))
) -> TeacherRead:
    if teacher_id == 'me':
        teacher_id = caller.id

    try:
        teacher = await teacher_service.get_by_id(teacher_id, caller)
    except exceptions.TeacherNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except exceptions.TeacherPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    return model_to_read_dto(teacher)


@router.get("/{teacher_id}/schedule")
async def get_teacher_weekly_schedule(
        teacher_id: int | Literal["me"],
        offset: int = 0,
        caller: UserIdentity = Depends(current_user),
        teacher_service: TeacherService = Depends(Stub(TeacherService))
) -> PaginationResponse:
    try:
        schedule = await teacher_service.get_schedule_by_id(teacher_id, offset, caller)
    except exceptions.TeacherNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    uri_prefix = f"{router.prefix}/{teacher_id}/schedule"
    return PaginationResponse(
        next_url=f"{uri_prefix}?offset={offset + 1}",
        prev_url=f"{uri_prefix}?offset={offset - 1}",
        data=schedule,
    )


@router.get("/{teacher_id}/competencies")
async def get_teacher_competencies(
        teacher_id: int | Literal['me'],
        caller: UserIdentity = Depends(current_user),
        teacher_service: TeacherService = Depends(Stub(TeacherService))
) -> list[str]:
    try:
        competencies: list[Competence] = await teacher_service.get_competencies(
            teacher_id,
            caller
        )
    except exceptions.TeacherPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    return [c.subject.name for c in competencies]
