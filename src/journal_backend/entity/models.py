from .academic_reports.models import AcademicReport
from .classes.models import Class, Classroom
from .students.models import Group, Student
from .teachers.models import Competence, Subject, Teacher
from .users.models import UserIdentity

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
