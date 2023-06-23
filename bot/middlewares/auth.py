from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message

from db.requests import find_user
from handlers.auth import auth_email, get_refresh_token


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:

        state = await data.get('state').get_data()
        if not state.get('headers'):
            user = await find_user(telegram_id=event.from_user.id)

            if user:
                token = await get_refresh_token(event, user)

                user_data = {
                    'user': user,
                    'headers':
                    {
                        'Authorization': 'Bearer ' + f'{token.get("access")}'
                    }
                }
                await data.get('state').update_data(data=user_data)

            else:
                return await auth_email(event, data.get('state'))

        return await handler(event, data)
