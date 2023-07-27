import logging

from aiogram import Bot, types

from utils.exceptions import ApplicationError


async def errors_handler(
    err_event: types.ErrorEvent, bot: Bot, event_chat: types.Chat
) -> bool:
    if isinstance(err_event.exception, ApplicationError):
        await bot.send_message(event_chat.id, err_event.exception.detail)
        return True
    logging.error(
        f'Ошибка при обработке запроса {err_event.update.update_id}: '
        f'{err_event.exception}'
    )
    await bot.send_message(event_chat.id, 'Извините, что-то пошло не так!')
    return True
