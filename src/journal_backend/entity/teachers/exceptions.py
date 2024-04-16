class TeacherNotFound(Exception):
    def __str__(self):
        return "Teacher not found"


class TeacherPermissionError(Exception):
    def __str__(self):
        return "Only admins can perform this action"
