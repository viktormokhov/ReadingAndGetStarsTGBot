from starlette.authentication import (
    AuthenticationBackend,
    AuthCredentials,
    SimpleUser
)
from starlette.requests import HTTPConnection

from config.settings import get_backend_settings

backend_settings = get_backend_settings()


class APIKeyAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn: HTTPConnection):
        api_key = conn.headers.get("x-api-key")
        if not api_key:
            return

        if api_key == backend_settings.api_key:
            return AuthCredentials(["authenticated", "admin"]), SimpleUser("admin")
        else:
            return AuthCredentials(["authenticated"]), SimpleUser("user")
