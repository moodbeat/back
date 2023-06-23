from __future__ import annotations

import requests
from aiogram import Router
from aiogram.filters import Text
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    Message
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config_reader import config
from middlewares.auth import AuthMiddleware


router = Router()

router.message.middleware(AuthMiddleware())


class HelpState(StatesGroup):
    title = State()
    description = State()
    recipient = State()


@router.message(Command('need_help'))
async def cmd_needhelp(message: Message, state: FSMContext):
    data = await state.get_data()
    headers = data.get('headers')
    response = requests.get(
        config.base_endpoint + 'users/current_user/', headers=headers
    ).json()
    msg_text = f'Привет, {response["first_name"]}!\nУкажите тему обращения.'
    await state.set_state(HelpState.title)
    await message.answer(msg_text)


@router.message(HelpState.title)
async def needhelp_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    msg_text = 'А теперь укажите описание проблемы.'
    await state.set_state(HelpState.description)
    await message.answer(msg_text)


@router.message(HelpState.description)
async def needhelp_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    msg_text = 'Выберите, кому хотите направить обращение.'
    data = await state.get_data()
    headers = data.get('headers')
    response = requests.get(
        config.base_endpoint + 'socials/specialists/', headers=headers
    ).json()

    keyboard = InlineKeyboardBuilder()
    for data in response:
        text = (
            f'{data.get("role")}, '
            f'{data.get("last_name")} {data.get("first_name")}'
        )
        keyboard.row(
            InlineKeyboardButton(
                text=text,
                callback_data=f'needhelp_{data.get("id")}'
            )
        )
    await state.set_state(HelpState.recipient)
    await message.answer(msg_text, reply_markup=keyboard.as_markup())


@router.callback_query(Text(startswith='needhelp_'))
@router.message(HelpState.recipient)
async def needhelp_recipient(callback: CallbackQuery, state: FSMContext):
    recipient_id = int(callback.data.split('_')[1])
    await state.update_data(recipient=recipient_id)
    await callback.message.delete()
    await callback.message.answer('Обращение сформировано.')
    await state.clear()
    # TODO добавить сохранение данных в бд апишки
