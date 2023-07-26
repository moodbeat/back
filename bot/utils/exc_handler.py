import logging

from aiogram import types

from utils.exceptions import ApplicationError


async def errors_handler(err_event: types.ErrorEvent) -> bool:
    if isinstance(err_event.exception, ApplicationError):
        if err_event.update.message:
            await err_event.update.message.answer(err_event.exception.detail)
        return True
    logging.error(
        f'Ошибка при обработке запроса {err_event.update.update_id}: '
        f'{err_event.exception}'
    )
    text = 'Извините, что-то пошло не так!'
    if err_event.update.message:
        await err_event.update.message.answer(text)
    elif err_event.update.callback_query:
        await err_event.update.callback_query.message.answer(text)
    return True
