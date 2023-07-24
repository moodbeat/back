from urllib.parse import urljoin

from aiogram.fsm.context import FSMContext

from config_reader import config

from .api.api_request import make_get_request
from .api.response_models import (AccessTokenRefreshResponse,
                                  AuthTokensPostResponse,
                                  CurrentUserGetResponse)
from .api_service import get_headers_from_storage
from .storage_service import get_object_from_storage, save_object_in_storage


async def get_current_user(state: FSMContext) -> CurrentUserGetResponse:
    """Выполняет запрос к API и возвращает объект текущего пользователя."""
    headers = await get_headers_from_storage(state)
    data = await make_get_request(
        urljoin(config.BASE_ENDPOINT, 'users/current_user/'),
        headers=headers.dict()
    )
    return CurrentUserGetResponse(**data)


async def get_current_user_from_storage(
    state: FSMContext
) -> CurrentUserGetResponse | None:
    """Возвращает объект пользователя из хранилища контекстных данных.

    При отсутствии данных вовзращает None.
    """
    return await get_object_from_storage(
        key='user',
        model=CurrentUserGetResponse,
        state=state
    )


async def save_current_user_in_storage(
    obj: CurrentUserGetResponse,
    state: FSMContext
) -> None:
    """Сохраняет объект пользователя в хранилище контекстных данных."""
    await save_object_in_storage(
        key='user',
        obj=obj,
        state=state
    )


async def update_tokens_of_current_user_in_storage(
    tokens_data: AccessTokenRefreshResponse | AuthTokensPostResponse,
    state: FSMContext
) -> bool:
    """Обновляет токены пользователя в хранилище контекстных данных.

    Если пользователь существует в контекстном хранилище - обновляет
    токен/токены и возвращает `True`.
    В случае отсутствия пользователя в хранилище - возвращает `False`.
    """
    current_user = await get_current_user_from_storage(state)
    if current_user:
        data = current_user.dict() | tokens_data.dict()
        update_user = CurrentUserGetResponse(
            **data
        )
        await save_current_user_in_storage(update_user, state)
        return True
    return False
