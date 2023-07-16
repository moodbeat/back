from aiogram.fsm.context import FSMContext

from config_reader import config

from .api.api_request import get_headers, make_get_request, make_post_request
from .api.request_models import NeedHelpPostRequest
from .api.response_models import HelpSpecialistGetResponse, HelpTypeGetResponse


async def get_specialists(
    state: FSMContext
) -> list[HelpSpecialistGetResponse]:
    headers = await get_headers(state)
    data = await make_get_request(
        config.BASE_ENDPOINT + 'socials/specialists/',
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
        f'{config.BASE_ENDPOINT}socials/help_types/?user={specialist_id}',
        headers=headers
    )
    return [
        HelpTypeGetResponse(**item) for item in data
    ]


async def post_need_help_data(
    user_data: dict,
    state: FSMContext
) -> None:
    data = NeedHelpPostRequest(**user_data)
    headers = await get_headers(state)
    await make_post_request(
        config.BASE_ENDPOINT + 'socials/need_help/',
        data=data.dict(),
        headers=headers
    )
