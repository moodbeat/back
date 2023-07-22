from urllib.parse import urljoin

from aiogram.fsm.context import FSMContext

from config_reader import config

from .api.api_request import get_headers, make_get_request
from .api.response_models import FullEventGetResponse, ShortEventGetResponse


async def get_events(
    state: FSMContext
) -> list[ShortEventGetResponse] | None:
    """Выполняет запрос к API и возвращает список мероприятий."""
    headers = await get_headers(state)
    data = await make_get_request(
        urljoin(config.BASE_ENDPOINT, 'events/'),
        headers=headers
    )
    if data.get('count') == 0:
        return None
    return [
        ShortEventGetResponse(**item) for item in data.get('results')
    ]


async def get_event_by_id(
    event_id: int,
    state: FSMContext
) -> FullEventGetResponse:
    """Выполняет запрос к API и возвращает объект запроса по id."""
    headers = await get_headers(state)
    data = await make_get_request(
        urljoin(config.BASE_ENDPOINT, f'events/{event_id}/'),
        headers=headers
    )
    return FullEventGetResponse(**data)
