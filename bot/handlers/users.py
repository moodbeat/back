import requests
from aiogram import Router
from aiogram.filters import Text
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config_reader import config
from middlewares.auth import AuthMiddleware


router = Router()

router.message.middleware(AuthMiddleware())


async def mood_keyboard():
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


@router.message(Command('mood'))
async def cmd_start(message: Message, state: FSMContext):
    state = await state.get_data()
    headers = state.get('headers')
    response = requests.get(
        config.base_endpoint + 'users/current_user/', headers=headers
    ).json()

    if response['latest_condition'] is None:
        keyboard = await mood_keyboard()
        await message.answer(
            f'Привет, {response["first_name"]}!\n\n'
            'Вы ещё не оценивали своё настроение. Предлагаем Вам как можно '
            'скорее его оценить.',
            reply_markup=keyboard.as_markup()
        )
    else:
        await message.answer(
            f'Привет, {response["first_name"]}!\n\n'
            'Актуальная оценка состояния по 5-ти балльной шкале: '
            f'{response["latest_condition"]["mood"]}'
        )


@router.callback_query(Text(startswith='mood_'))
async def get_survey(callback: CallbackQuery, state: FSMContext):
    mood_id = int(callback.data.split('_')[1])
    # TODO добавить сохранение данных в бд апишки
    await callback.message.delete()
    await callback.message.answer('Вы оценили своё состояние.')
