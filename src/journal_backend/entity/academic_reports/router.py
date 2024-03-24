from dependencies import current_student
from fastapi import APIRouter, Depends
from journal_backend.entity.users.students.models import Student

router = APIRouter(prefix="/academic_reports")


@router.get("/")
async def get_academic_reports(student: Student = Depends(current_student)):
    return {"data": student.academic_reports}  # will be replaced with pagination
