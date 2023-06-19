import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config_reader import config
from handlers import auth, base, entries, events, surveys, need_help, users
from handlers.bot_commands import set_bot_commands


async def main():
    logging.basicConfig(level=logging.INFO)
    storage = MemoryStorage()

    bot = Bot(token=config.telegram_token.get_secret_value())
    dp = Dispatcher(storage=storage)

    dp.include_routers(
        auth.router,
        base.router,
        entries.router,
        events.router,
        need_help.router,
        surveys.router,
        users.router,
    )

    await set_bot_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
