from typing import Union

from aiogram.fsm.context import FSMContext

from config_reader import config
from db.requests import find_user, update_auth_data

from .base_session import get_client_session
from .request_models import AuthTokenRefreshPostRequest
from .response_models import AuthTokenPostResponse

sessions_generator = get_client_session()


async def post_token_refresh(refresh: str) -> AuthTokenPostResponse:
    data = AuthTokenRefreshPostRequest(refresh=refresh)
    return await make_post_request(
        config.BASE_ENDPOINT + 'auth/jwt/refresh/',
        data=data.dict(),
        headers=None
    )


async def refresh_token(url: str, headers: str) -> Union[None, dict]:
    session = await sessions_generator.asend(None)
    access_token = headers['Authorization'].split('Bearer ')[1]
    user = await find_user(access_token=access_token)
    if user:
        token = await post_token_refresh(refresh=user.refresh_token)
        headers['Authorization'] = 'Bearer ' + f'{token.get("access")}'
        await update_auth_data(
            user.id, access_token=token.get('access')
        )
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            return await response.json()
    return None


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
