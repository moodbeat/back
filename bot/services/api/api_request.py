from typing import Any, AsyncGenerator

from aiohttp import ClientSession

from .base_session import get_client_session

sessions_generator: AsyncGenerator[ClientSession, None] = get_client_session()


async def make_get_request(url: str, headers: dict) -> dict[str, Any]:
    session: ClientSession = await sessions_generator.asend(None)
    async with session.get(url, headers=headers) as response:
        response.raise_for_status()
        return await response.json()


async def make_post_request(
    url: str,
    data: dict,
    headers: dict[str, Any] | dict = {}
) -> dict[str, Any] | None:
    session: ClientSession = await sessions_generator.asend(None)
    async with session.post(url, json=data, headers=headers) as response:
        response.raise_for_status()
        return await response.json()
