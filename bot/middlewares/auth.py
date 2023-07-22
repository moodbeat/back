from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message

from db.requests import find_user
from handlers.auth import auth_email


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any]
    ) -> Any:
        state = await data.get('state').get_data()

        if not state.get('headers'):
            user = await find_user(telegram_id=event.from_user.id)

            if user:
                user_data = {
                    'headers':
                    {
                        'Authorization': 'Bearer ' + f'{user.access_token}'
                    }
                }
                await data.get('state').update_data(user_data)

            else:
                return await auth_email(event, data.get('state'))

        return await handler(event, data)
