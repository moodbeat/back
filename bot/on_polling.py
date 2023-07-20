import logging

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage

from bot_commands import set_bot_commands
from config_reader import config
from handlers import auth, base, conditions, entries, events, hot_line, surveys


async def main():
    logging.basicConfig(level=logging.INFO)
    storage = MemoryStorage()

    bot = Bot(token=config.TELEGRAM_TOKEN.get_secret_value())
    dp = Dispatcher(storage=storage)

    @dp.errors()
    async def errors_handler(err_event: types.ErrorEvent):
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

    dp.include_routers(
        auth.router,
        base.router,
        entries.router,
        events.router,
        hot_line.router,
        surveys.router,
        conditions.router,
    )

    await set_bot_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
