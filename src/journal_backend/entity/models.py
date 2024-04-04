from .academic_reports.models import AcademicReport
from .classes.models import Class, Classroom
from .users.models import UserIdentity
from .teachers.models import Competence, Subject, Teacher
from .students.models import Student, Group

__all__ = (
    "AcademicReport",
    "Class",
    "Classroom",
    "UserIdentity",
    "Student",
    "Group",
    "Teacher",
    "Competence",
    "Subject"
)
