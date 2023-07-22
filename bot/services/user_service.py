from urllib.parse import urljoin

from aiogram.fsm.context import FSMContext

from config_reader import config

from .api.api_request import get_headers, make_get_request
from .api.response_models import CurrentUserGetResponse


async def get_current_user(state: FSMContext) -> CurrentUserGetResponse:
    headers = await get_headers(state)
    data = await make_get_request(
        urljoin(config.BASE_ENDPOINT, 'users/current_user/'),
        headers=headers
    )
    return CurrentUserGetResponse(**data)
