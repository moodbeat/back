from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery
from db.requests import get_user_by_telegram_id


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:

        state = await data.get('state').get_data()
        if not state.get('tokens'):
            user = await get_user_by_telegram_id(event.from_user.id)

            if user:
                user_data = {
                    'tokens':
                    {
                        'access': user.access_token,
                        'refresh': user.refresh_token
                    }
                }
                await data.get('state').update_data(data=user_data)
            else:
                await event.answer(
                    'Вы не авторизованы. Введите /auth, чтобы авторизоваться.'
                )
                return

        return await handler(event, data)
