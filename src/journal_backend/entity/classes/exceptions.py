class ClassNotFound(Exception):
    def __str__(self) -> str:
        return 'Class not found for the provided student'
