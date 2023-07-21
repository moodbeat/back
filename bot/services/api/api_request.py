from typing import Union

from aiogram.fsm.context import FSMContext

from config_reader import config
from db.requests import delete_user, find_user, update_auth_data

from .base_session import get_client_session
from .request_models import AuthTokenRefreshRequest
from .response_models import AuthTokenPostResponse

sessions_generator = get_client_session()


async def token_refresh_by_telegram(
    email: str,
    telegram_id: int
) -> AuthTokenPostResponse:
    data = AuthTokenRefreshRequest(email=email, telegram_id=telegram_id)
    try:
        return await make_post_request(
            config.BASE_ENDPOINT + 'auth/jwt/telegram_create/',
            data=data.dict(),
            headers=None
        )
    except Exception as error:
        if error.code == 400:
            user = await find_user(telegram_id=telegram_id, email=email)
            await delete_user(id=user.id)


async def refresh_token(url: str, headers: str) -> Union[None, dict]:
    session = await sessions_generator.asend(None)
    access_token = headers['Authorization'].split('Bearer ')[1]
    user = await find_user(access_token=access_token)
    tokens = await token_refresh_by_telegram(
        email=user.email, telegram_id=user.telegram_id
    )
    headers['Authorization'] = 'Bearer ' + f'{tokens.get("access")}'
    await update_auth_data(
        user.id,
        access_token=tokens.get('access'),
        refresh_token=tokens.get('refresh')
    )
    async with session.get(url, headers=headers) as response:
        response.raise_for_status()
        return await response.json()


async def make_get_request(url: str, headers: dict) -> dict:
    session = await sessions_generator.asend(None)
    async with session.get(url, headers=headers) as response:

        if response.status == 401:
            return await refresh_token(url, headers)

        response.raise_for_status()
        return await response.json()


async def make_post_request(
    url: str,
    data: dict,
    headers: Union[None, dict]
) -> Union[None, dict]:
    session = await sessions_generator.asend(None)
    async with session.post(url, json=data, headers=headers) as response:

        if response.status == 401:
            return await refresh_token(url, headers)

        response.raise_for_status()
        return await response.json()


async def get_headers(state: FSMContext) -> dict:
    state = await state.get_data()
    return state.get('headers')


async def make_post_request_with_return_data(
    url: str, data: dict, headers: dict
) -> None:
    session = await sessions_generator.asend(None)
    async with session.post(url, json=data, headers=headers) as response:
        response.raise_for_status()
        return await response.json()
