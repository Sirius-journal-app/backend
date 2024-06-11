from fastapi_users.password import PasswordHelper
from sqlalchemy.orm import sessionmaker
from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.auth import AuthProvider
from starlette_admin.exceptions import LoginFailed, FormValidationError

from journal_backend.entity.users.enums import Role
from journal_backend.entity.users.models import UserIdentity
from journal_backend.entity.users.repository import UserRepository


class MyAuthProvider(AuthProvider):
    def __init__(self, session_factory: sessionmaker, **kwargs):
        super().__init__(**kwargs)
        self.session_factory = session_factory
        self._password_helper = PasswordHelper()

    async def login(
            self,
            username: str,
            password: str,
            remember_me: bool,
            request: Request,
            response: Response,
    ) -> Response:
        if len(username) < 3:
            # Form data validation
            raise FormValidationError(
                {"username": "Ensure username has at least 03 characters"}
            )

        async with self.session_factory() as session:
            user_repo = UserRepository(session, UserIdentity)

            user = await user_repo.get_by_email(username)
            if not user or user.role != Role.ADMIN:
                # Run the hasher to mitigate timing attack
                # Inspired from Django: https://code.djangoproject.com/ticket/20760
                self._password_helper.hash(password)
                raise LoginFailed("Invalid username or password")

            verified, updated_password_hash = self._password_helper.verify_and_update(
                password, user.hashed_password
            )
            if not verified:
                raise LoginFailed("Invalid username or password")

            # Update password hash to a more robust one if needed
            if updated_password_hash is not None:
                await user_repo.update(user, {"hashed_password": updated_password_hash})

            request.session.update({"username": username})
            return response

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response

    async def is_authenticated(self, request: Request) -> bool:
        if request.session.get("username", None) is not None:
            request.state.user = request.session.get("username")
            return True
        return False
