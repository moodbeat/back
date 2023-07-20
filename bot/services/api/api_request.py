from aiogram.fsm.context import FSMContext

from .base_session import get_client_session

sessions_generator = get_client_session()


async def make_get_request(url: str, headers: dict) -> dict:
    session = await sessions_generator.asend(None)
    async with session.get(url, headers=headers) as response:
        response.raise_for_status()
        return await response.json()


async def make_post_request(url: str, data: dict, headers: dict) -> None:
    session = await sessions_generator.asend(None)
    async with session.post(url, json=data, headers=headers) as response:
        response.raise_for_status()


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
