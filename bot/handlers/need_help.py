from __future__ import annotations

from aiogram import Router
from aiogram.filters import Text
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config_reader import config
from middlewares.auth import AuthMiddleware
from services.api_request import (get_headers, make_get_request,
                                  make_post_request)
from services.request_models import NeedHelpPostRequest

router = Router()

router.message.middleware(AuthMiddleware())


class HelpState(StatesGroup):
    recipient = State()
    type = State()
    comment = State()


@router.message(Command('need_help'))
async def cmd_needhelp(message: Message, state: FSMContext):
    headers = await get_headers(state)
    response = await make_get_request(
        config.base_endpoint + 'users/current_user/',
        headers=headers
    )
    msg_text = (
        f'Привет, {response["first_name"]}!\n'
        'Выберите, кому хотите направить обращение.'
    )
    response = await make_get_request(
        config.base_endpoint + 'socials/specialists/',
        headers=headers
    )

    keyboard = InlineKeyboardBuilder()
    for data in response:
        text = (
            f'{data.get("role")}, '
            f'{data.get("last_name")} {data.get("first_name")}'
        )
        keyboard.row(
            InlineKeyboardButton(
                text=text,
                callback_data=f'recipient_{data.get("id")}'
            )
        )
    keyboard.row(
        InlineKeyboardButton(text='На главную', callback_data='back_start')
    )
    await state.set_state(HelpState.recipient)
    await message.answer(
        msg_text,
        reply_markup=keyboard.as_markup()
    )


@router.callback_query(Text(startswith='recipient_'))
@router.message(HelpState.recipient)
async def needhelp_recipient(callback: CallbackQuery, state: FSMContext):
    recipient_id = int(callback.data.split('_')[1])
    await state.update_data(recipient=recipient_id)
    await callback.message.delete()
    headers = await get_headers(state)
    response = await make_get_request(
        f'{config.base_endpoint}socials/help_types/?user={recipient_id}',
        headers=headers
    )

    msg_text = 'А теперь выберите тип обращения.'
    keyboard = InlineKeyboardBuilder()
    for data in response:
        text = (data.get('title'))
        keyboard.row(
            InlineKeyboardButton(
                text=text,
                callback_data=f'type_{data.get("id")}'
            )
        )
    keyboard.row(
        InlineKeyboardButton(text='На главную', callback_data='back_start')
    )

    await state.set_state(HelpState.type)
    await callback.message.answer(
        msg_text,
        reply_markup=keyboard.as_markup()
    )


@router.callback_query(Text(startswith='type_'))
@router.message(HelpState.type)
async def needhelp_type(callback: CallbackQuery, state: FSMContext):
    type_id = int(callback.data.split('_')[1])
    await state.update_data(type=type_id)
    await callback.message.delete()

    msg_text = 'А теперь опишите проблему.'
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text='На главную', callback_data='back_start')
    )
    await state.set_state(HelpState.comment)
    await callback.message.answer(
        msg_text,
        reply_markup=keyboard.as_markup()
    )


@router.message(HelpState.comment)
async def needhelp_comment(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    user_data = await state.get_data()
    data = NeedHelpPostRequest(**user_data)
    headers = await get_headers(state)
    await make_post_request(
        config.base_endpoint + 'socials/need_help/',
        data=data.dict(),
        headers=headers
    )
    await message.answer('Обращение сформировано и отправлено.')
    await state.set_state(state=None)
