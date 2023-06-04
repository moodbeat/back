import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config_reader import config
from handlers import auth, base


async def main():
    logging.basicConfig(level=logging.INFO)
    storage = MemoryStorage()

    bot = Bot(token=config.telegram_token.get_secret_value())
    dp = Dispatcher(storage=storage)

    dp.include_routers(base.router, auth.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
