from urllib.parse import urljoin

from config_reader import config

from .api.api_request import (make_post_request,
                              make_post_request_with_return_data)
from .api.request_models import AuthCodePostRequest, AuthTokenPostRequest
from .api.response_models import AuthTokenPostResponse


async def post_auth_code_response(email: str) -> None:
    """Выполняет POST-запрос к API с электронной почтой пользователя."""
    data = AuthCodePostRequest(email=email)
    await make_post_request(
        urljoin(config.BASE_ENDPOINT, 'users/send_telegram_code/'),
        data=data.dict(),
        headers=None
    )


async def post_token_create(
    email: str,
    code: int,
    telegram_id: int
) -> AuthTokenPostResponse:
    """Выполняет POST-запрос к API с данными пользователя.

    Возвращает в ответ access- и refresh- токены.
    """
    data = AuthTokenPostRequest(
        email=email,
        code=code,
        telegram_id=telegram_id
    )
    result = await make_post_request_with_return_data(
        urljoin(config.BASE_ENDPOINT, 'auth/jwt/telegram_create/'),
        data=data.dict(),
        headers=None
    )
    return AuthTokenPostResponse(**result)
