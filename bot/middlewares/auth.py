from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from handlers.auth import cmd_auth
from services.api_service import (get_headers_from_storage,
                                  save_headers_in_storage)
from services.user_service import get_current_user_from_storage


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any]
    ) -> Any:
        state: FSMContext = data.get('state')
        headers = await get_headers_from_storage(state)

        if not headers:
            user = await get_current_user_from_storage(state)

            if user:
                headers = {'Authorization': 'Bearer ' + {user.access}}
                await save_headers_in_storage(headers, state)
            else:
                return await cmd_auth(event, state)

        return await handler(event, data)
