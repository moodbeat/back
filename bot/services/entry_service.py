from aiogram.fsm.context import FSMContext

from config_reader import config

from .api.api_request import get_headers, make_get_request
from .api.response_models import FullEntryGetResponse, ShortEntryGetResponse


async def get_last_ten_entries(
    state: FSMContext
) -> list[ShortEntryGetResponse] | None:
    headers = await get_headers(state)
    data = await make_get_request(
        config.BASE_ENDPOINT + 'entries/?limit=10',
        headers=headers
    )
    if data.get('count') == 0:
        return None
    return [
        ShortEntryGetResponse(**item) for item in data.get('results')
    ]


async def get_entry_by_id(
    entry_id: int,
    state: FSMContext
) -> FullEntryGetResponse:
    headers = await get_headers(state)
    url = config.BASE_ENDPOINT + f'entries/{entry_id}/'
    data = await make_get_request(
        url,
        headers=headers
    )
    return FullEntryGetResponse(entry_url=url, **data)
