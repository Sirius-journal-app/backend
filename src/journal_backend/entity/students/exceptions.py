class StudentNotFound(Exception):
    def __str__(self):
        return "Student not found"


class StudentPermissionError(Exception):
    def __str__(self):
        return "Only admins and teachers can perform this action"


class GroupNotFound(Exception):
    def __str__(self):
        return "Group with such name was not found"

