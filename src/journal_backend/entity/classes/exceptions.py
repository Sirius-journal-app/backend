class ClassNotFound(Exception):
    def __str__(self):
        return 'Class not found for the provided student'
