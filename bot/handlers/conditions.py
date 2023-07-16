from datetime import datetime

from aiogram import Router
from aiogram.filters import Text
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config_reader import config
from middlewares.auth import AuthMiddleware
from services.condition_service import (get_current_user_with_condition,
                                        post_condition_data)

router = Router()

router.message.middleware(AuthMiddleware())


def mood_keyboard():
    keyboard = InlineKeyboardBuilder()
    buttons = []
    for id, emoji in enumerate('☹🙁😐🙂😃', start=1):
        buttons.append(InlineKeyboardButton(
            text=emoji,
            callback_data=f'mood_{id}'
        )
        )
    keyboard.row(*buttons)
    return keyboard


@router.message(Command('conditions'))
async def cmd_conditions(message: Message, state: FSMContext):
    user = await get_current_user_with_condition(state)
    tz = config.get_timezone
    keyboard = mood_keyboard()

    if not user.latest_condition:
        await message.answer(
            f'Привет, {user.first_name}!\n\n'
            'Вы ещё не оценивали своё настроение.\n'
            'Предлагаем Вам как можно '
            'скорее это сделать.',
            reply_markup=keyboard.as_markup()
        )
    elif (
        datetime.now(tz) - user.latest_condition.date
    ).total_seconds() > config.CONDITION_PERIOD_SEC:
        await message.answer(
            f'Привет, {user.first_name}!\n\n'
            'Вы давно не оценивали своё настроение.\n'
            'Предлагаем Вам как можно '
            'скорее это сделать.',
            reply_markup=keyboard.as_markup()
        )
    else:
        mood = '☹🙁😐🙂😃'
        await message.answer(
            f'Привет, {user.first_name}!\n\n'
            'Вам пока рано оценивать свое состояние.\n'
            'Ваша актуальная оценка состояния по 5-ти бальной шкале: '
            f'{user.latest_condition.mood}\n'
            f'{mood[user.latest_condition.mood - 1]}'
        )


@router.callback_query(Text(startswith='mood_'))
async def get_condition(callback: CallbackQuery, state: FSMContext):
    mood = int(callback.data.split('_')[1])
    await post_condition_data(mood, state)
    await callback.message.delete()
    await callback.message.answer('Вы оценили своё состояние')