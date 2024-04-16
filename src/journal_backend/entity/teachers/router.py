import fastapi_users.router
from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from journal_backend.depends_stub import Stub
from journal_backend.entity.teachers.dto import TeacherCreate
from journal_backend.entity.teachers.service import TeacherService
from journal_backend.entity.users import exceptions

router = APIRouter(prefix="/teachers")


@router.post("")
async def register(
        teacher_body: TeacherCreate,
        teacher_service: TeacherService = Depends(Stub(TeacherService))
):
    try:
        teacher = await teacher_service.create(teacher_create=teacher_body)
    except exceptions.UserAlreadyExists as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return teacher.id
