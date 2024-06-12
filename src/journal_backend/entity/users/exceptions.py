class UserAlreadyExists(Exception):
    def __str__(self) -> str:
        return "User with such email already exists"


class InvalidConfirmationToken(Exception):
    def __str__(self) -> str:
        return "Confirmation token is not exist or expired"


class InvalidIdentity(Exception):
    def __str__(self) -> str:
        return "You can not confirm email of the other person"
