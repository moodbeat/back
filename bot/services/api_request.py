from datetime import datetime

import aiohttp
from aiogram.fsm.context import FSMContext


async def make_get_request(url: str, headers: dict) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return await response.json()


async def make_post_request(url: str, data: dict, headers: dict) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as response:
            response.raise_for_status()


async def get_headers(state: FSMContext) -> dict:
    state = await state.get_data()
    return state.get('headers')


def format_date(date: str) -> str:
    date = datetime.fromisoformat(date)
    return date.strftime('%d.%m.%Y %H:%M')
