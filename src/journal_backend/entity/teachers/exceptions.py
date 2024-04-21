class TeacherNotFound(Exception):
    def __str__(self) -> str:
        return "Teacher not found"


class TeacherPermissionError(Exception):
    def __str__(self) -> str:
        return "Only admins can perform this action"
