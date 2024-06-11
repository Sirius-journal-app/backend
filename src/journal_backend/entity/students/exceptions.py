class StudentNotFound(Exception):
    def __str__(self) -> str:
        return "Student not found"


class StudentPermissionError(Exception):
    def __str__(self) -> str:
        return "Only admins and teachers can perform this action"


class GroupNotFound(Exception):
    def __str__(self) -> str:
        return "Group with such name was not found"


class InvalidConfirmationToken(Exception):
    def __str__(self) -> str:
        return "Confirmation token is not exist or expired"


class InvalidIdentity(Exception):
    def __str__(self) -> str:
        return "You can not confirm email of the other person"
