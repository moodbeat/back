from aiogram import Router, types
from aiogram.filters.command import Command
from middlewares.auth import AuthMiddleware

router = Router()

router.message.middleware(AuthMiddleware())


@router.message(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer('Ну типа старт?')
