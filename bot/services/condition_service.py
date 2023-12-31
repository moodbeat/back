from urllib.parse import urljoin

from aiogram.fsm.context import FSMContext

from config_reader import config

from .api.api_request import make_get_request, make_post_request
from .api.request_models import ConditionPostRequest
from .api.response_models import UserConditionGetResponse
from .api_service import get_headers_from_storage


async def get_current_user_with_condition(
    state: FSMContext
) -> UserConditionGetResponse:
    """Выполняет запрос к API.

    Возвращает объект пользователя со временем последней оценки
    своего состояния.
    """
    headers = await get_headers_from_storage(state)
    data = await make_get_request(
        urljoin(config.BASE_ENDPOINT, 'users/current_user/'),
        headers=headers.dict()
    )
    return UserConditionGetResponse(**data)


async def post_condition_data(
    mood: int,
    state: FSMContext
) -> None:
    """Выполняет POST-запрос к API.

    Отправляет результаты оценки пользователем своего состояния.
    """
    data = ConditionPostRequest(mood=mood)
    headers = await get_headers_from_storage(state)
    await make_post_request(
        urljoin(config.BASE_ENDPOINT, 'metrics/conditions/'),
        data=data.dict(),
        headers=headers.dict()
    )
