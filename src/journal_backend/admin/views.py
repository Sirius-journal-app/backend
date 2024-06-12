from datetime import timedelta, time
from typing import Any

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette_admin import TimeField, RequestAction, BaseField, EmailField, PasswordField
from starlette_admin.contrib.sqla import ModelView
from starlette_admin.exceptions import FormValidationError

from journal_backend.entity.teachers.models import Teacher


class ClassView(ModelView):
    fields = [
        "id",  # type:ignore
        "starts_at",  # type:ignore
        TimeField("duration"),
        "group",  # type:ignore
        "teacher",  # type:ignore
        "classroom",  # type:ignore
        "subject",  # type:ignore
    ]

    async def validate(self, request: Request, data: dict[str, Any]) -> None:
        errors: dict[str | int, Any] = {}
        session: AsyncSession = request.state.session

        subject_name = data['subject'].name
        teacher = await session.get(Teacher, data['teacher'].id)
        if not teacher:
            return

        if subject_name not in [c.subject.name for c in teacher.competencies]:
            teacher = teacher.identity
            errors['subject'] = (f'Teacher {teacher.surname.title()} {teacher.name.title()} '
                                 f'has no competence for this subject')
            raise FormValidationError(errors)

        duration: time = data['duration']
        data['duration'] = timedelta(hours=duration.hour, minutes=duration.minute)

        return await super().validate(request, data)

    async def serialize_field_value(
            self, value: Any, field: BaseField, action: RequestAction, request: Request
    ) -> Any:
        if isinstance(value, timedelta):
            value = time(hour=value.seconds // 3600, minute=(value.seconds % 3600) // 60)
        """
        Format output value for each field.

        !!! important

            The returned value should be json serializable

        Parameters:
            value: attribute of item returned by `find_all` or `find_by_pk`
            field: Starlette Admin field for this attribute
            action: Specify where the data will be used. Possible values are
                `VIEW` for detail page, `EDIT` for editing page and `API`
                for listing page and select2 data.
            request: The request being processed
        """
        if value is None:
            return await field.serialize_none_value(request, action)
        return await field.serialize_value(request, value, action)


class ClassRoomView(ModelView):
    fields = ["id", "name"]  # type:ignore


class SubjectView(ModelView):
    fields = ["id", "name"]  # type:ignore


class TeacherView(ModelView):
    fields = [
        "id",  # type:ignore
        "identity",  # type:ignore
        "qualification",  # type:ignore
        "education",  # type:ignore
        "competencies",  # type:ignore
    ]


class UserIdentityView(ModelView):
    fields = [
        "id",  # type:ignore
        "name",  # type:ignore
        "surname",  # type:ignore
        "role",  # type:ignore
        "date_of_birth",  # type:ignore
        "profile_photo_uri",  # type:ignore
        EmailField("email"),
        PasswordField("hashed_password", label='Password'),
    ]

    async def validate(self, request: Request, data: dict[str, Any]) -> None:
        context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        data['hashed_password'] = context.hash(data['hashed_password'])

        return await super().validate(request, data)
