from http import HTTPStatus
from typing import Any, Awaitable, Callable, Type

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject
from aiohttp.client_exceptions import ClientResponseError

from services.auth_service import update_jwt_tokens


class CheckAccessTokenStatusMiddleware(BaseMiddleware):
    """Контролирует статус токена доступа по ответу API.

    Задействует логику обновления токена/токенов в случае истечения
    срока их действия.
    """

    async def __call__(
        self,
        handler: Callable[
            [Type[TelegramObject], dict[str, Any]], Awaitable[Any]
        ],
        event: Type[TelegramObject],
        data: dict[str, Any]
    ) -> Any:
        try:
            await handler(event, data)
        except ClientResponseError as e:
            if e.status == HTTPStatus.UNAUTHORIZED:
                state: FSMContext = data.get('state')
                telegram_id: int = data.get('event_from_user').id
                await state.update_data(headers=None)
                await update_jwt_tokens(telegram_id, state)
                return await handler(event, data)
            raise
