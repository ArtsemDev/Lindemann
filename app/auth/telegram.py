import json
from typing import Callable, Any

from aiogram.utils.web_app import safe_parse_webapp_init_data, WebAppUser
from starlette.authentication import AuthenticationBackend, AuthCredentials, AuthenticationError
from starlette.requests import HTTPConnection


class TelegramWebappAuthenticationBackend(AuthenticationBackend):

    def __init__(self, token: str, loads: Callable[..., Any] = json.loads,) -> None:
        self.token = token
        self.loads = loads

    async def authenticate(
            self, conn: HTTPConnection
    ) -> tuple[AuthCredentials, WebAppUser] | None:
        telegram_init_data = conn.headers.get("Authorization")

        if telegram_init_data is None:
            return

        try:
            return AuthCredentials(["authenticated"]), safe_parse_webapp_init_data(
                token=self.token,
                init_data=telegram_init_data,
                loads=self.loads
            ).user
        except ValueError as e:
            raise AuthenticationError(e)
