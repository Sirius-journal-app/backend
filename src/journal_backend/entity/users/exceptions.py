class UserAlreadyExists(Exception):
    def __str__(self):
        return "User with such email already exists"
