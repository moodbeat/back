from typing import Any, Awaitable, Callable, Type

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import TelegramObject


class StateResetMiddleware(BaseMiddleware):
    """Сбрасывает состояния `State` пользователя в None.

    Данное иннер-мидлвайр будет сбрасывать состояние только
    при срабатывании хэндлеров сообщений типов: `Message`, `Callback_Query`,
    помеченных флагом `state_reset`.
    """

    async def __call__(
        self,
        handler: Callable[
            [Type[TelegramObject], dict[str, Any]], Awaitable[Any]
        ],
        event: Type[TelegramObject],
        data: dict[str, Any]
    ) -> Any:
        if get_flag(data, 'state_reset'):
            await data.get('state').set_state(state=None)
        return await handler(event, data)
