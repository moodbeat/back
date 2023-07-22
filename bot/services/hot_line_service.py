from urllib.parse import urljoin

from aiogram.fsm.context import FSMContext

from config_reader import config

from .api.api_request import get_headers, make_get_request, make_post_request
from .api.request_models import HotLinePostRequest
from .api.response_models import HelpSpecialistGetResponse, HelpTypeGetResponse


async def get_specialists(
    state: FSMContext
) -> list[HelpSpecialistGetResponse]:
    headers = await get_headers(state)
    data = await make_get_request(
        urljoin(config.BASE_ENDPOINT, 'socials/specialists/'),
        headers=headers
    )
    return [
        HelpSpecialistGetResponse(**item) for item in data
    ]


async def get_help_types_by_specialist_id(
    specialist_id: int,
    state: FSMContext
) -> list[HelpTypeGetResponse]:
    headers = await get_headers(state)
    data = await make_get_request(
        urljoin(
            config.BASE_ENDPOINT,
            f'socials/help_types/?user={specialist_id}'
        ),
        headers=headers
    )
    return [
        HelpTypeGetResponse(**item) for item in data
    ]


async def post_hot_line_data(
    user_data: dict,
    state: FSMContext
) -> None:
    data = HotLinePostRequest(**user_data)
    headers = await get_headers(state)
    await make_post_request(
        urljoin(config.BASE_ENDPOINT, 'socials/need_help/'),
        data=data.dict(),
        headers=headers
    )
