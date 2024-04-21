class UserAlreadyExists(Exception):
    def __str__(self) -> str:
        return "User with such email already exists"
