from http import HTTPStatus
from typing import Any
from urllib.parse import urljoin

from aiogram.fsm.context import FSMContext
from aiohttp.client_exceptions import ClientResponseError

from config_reader import config

from .api.api_request import make_post_request
from .api.request_models import (AccessTokenRefreshRequest,
                                 AuthCodePostRequest, AuthTokensPostRequest,
                                 AuthTokensRefreshRequest)
from .api.response_models import (AccessTokenRefreshResponse,
                                  AuthTokensPostResponse)
from .user_service import (get_current_user_from_storage,
                           update_tokens_of_current_user_in_storage)


async def post_auth_code(email: str) -> None:
    """Выполняет POST-запрос к API с электронной почтой пользователя."""
    data = AuthCodePostRequest(email=email)
    await make_post_request(
        urljoin(config.BASE_ENDPOINT, 'users/send_telegram_code/'),
        data=data.dict()
    )


async def post_token_create(
    user_data: dict[str, Any],
) -> AuthTokensPostResponse:
    """Выполняет POST-запрос к API с данными пользователя.

    Возвращает в ответ access- и refresh- токены.
    """
    data = AuthTokensPostRequest(**user_data)
    result = await make_post_request(
        urljoin(config.BASE_ENDPOINT, 'auth/jwt/telegram_create/'),
        data=data.dict()
    )
    return AuthTokensPostResponse(**result)


async def update_all_tokens_by_telegram_id(
    email: str,
    telegram_id: int
) -> AuthTokensPostResponse:
    data = AuthTokensRefreshRequest(email=email, telegram_id=telegram_id)
    result = await make_post_request(
        urljoin(config.BASE_ENDPOINT, 'auth/jwt/telegram_create/'),
        data=data.dict()
    )
    return AuthTokensPostResponse(**result)


async def update_access_token_by_refresh_token(
    refresh_token: str
) -> AccessTokenRefreshResponse:
    data = AccessTokenRefreshRequest(refresh=refresh_token)
    result = await make_post_request(
        urljoin(config.BASE_ENDPOINT, 'auth/jwt/refresh/'),
        data=data.dict()
    )
    return AccessTokenRefreshResponse(**result)


async def update_jwt_tokens(telegram_id: int, state: FSMContext) -> None:
    """При истечении срока действия токенов обновляет их."""
    user = await get_current_user_from_storage(state)
    try:
        response = await update_access_token_by_refresh_token(
            user.refresh
        )
    except ClientResponseError as e:
        if e.status == HTTPStatus.UNAUTHORIZED:
            try:
                response = await update_all_tokens_by_telegram_id(
                    user.email, telegram_id
                )
            except ClientResponseError as e:
                if e.status == HTTPStatus.NOT_FOUND:
                    await state.clear()
            else:
                await update_tokens_of_current_user_in_storage(
                    response, state
                )
    else:
        await update_tokens_of_current_user_in_storage(
            response, state
        )
