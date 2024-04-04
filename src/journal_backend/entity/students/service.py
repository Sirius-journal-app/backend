from journal_backend.entity.students.repository import StudentRepository


class StudentService:
    def __init__(
            self,
            repo: StudentRepository,
    ) -> None:
        self.repo = repo
