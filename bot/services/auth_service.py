from config_reader import config

from .api.api_request import (make_post_request,
                              make_post_request_with_return_data)
from .api.request_models import AuthCodePostRequest, AuthTokenPostRequest


async def post_auth_code_response(email: str) -> None:
    data = AuthCodePostRequest(email=email)
    await make_post_request(
        config.BASE_ENDPOINT + 'users/send_telegram_code/',
        data=data.dict(),
        headers=None
    )


async def post_token_create(
    email: str,
    code: int,
    telegram_id: int
) -> dict:
    data = AuthTokenPostRequest(
        email=email,
        code=code,
        telegram_id=telegram_id
    )
    return await make_post_request_with_return_data(
        config.BASE_ENDPOINT + 'auth/jwt/telegram_create/',
        data=data.dict(),
        headers=None
    )
