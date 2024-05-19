from dataclasses import dataclass
from datetime import datetime

from journal_backend.entity.classes.models import Class


@dataclass
class ClassRead:
    id: int
    group: str
    subject: str
    teacher: str
    classroom: str
    starts_at: datetime
    ends_at: datetime


@dataclass
class DailySchedule:
    day: int
    classes: list[ClassRead]


def to_read_dto(class_: Class) -> ClassRead:
    return ClassRead(
        id=class_.id,
        group=class_.group.name,
        subject=class_.subject.name,
        teacher=f"{class_.teacher.identity.surname} {class_.teacher.identity.name[0]}.",
        classroom=class_.classroom.name,
        starts_at=class_.starts_at,
        ends_at=class_.starts_at + class_.duration,
    )


def build_schedule_response(schedule_by_days: dict[int, list[Class]]) -> list[DailySchedule]:
    resp = []
    for day, classes in schedule_by_days.items():
        resp.append(DailySchedule(
            day=day,
            classes=[
                to_read_dto(class_)
                for class_ in classes
            ]))
    return resp
