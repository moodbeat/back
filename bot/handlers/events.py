from __future__ import annotations

from aiogram import Router
from aiogram.filters import Text
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config_reader import config
from handlers.api_request import format_date, get_headers, make_get_request
from middlewares.auth import AuthMiddleware

router = Router()

router.message.middleware(AuthMiddleware())


@router.callback_query(Text(startswith='back_events'))
@router.message(Command('events'))
async def cmd_events(message: Message | CallbackQuery, state: FSMContext):
    if isinstance(message, CallbackQuery):
        await message.message.delete()

    headers = await get_headers(state)
    response = await make_get_request(
        config.base_endpoint + 'events/',
        headers=headers
    )

    if response.get('count') == 0:
        return await message.answer(
            'На данный момент нет доступных мероприятий'
        )

    keyboard = InlineKeyboardBuilder()
    for data in response.get('results'):
        keyboard.row(
            InlineKeyboardButton(
                text=data.get('name'),
                callback_data=f'events_{data.get("id")}'
            )
        )
    keyboard.row(
        InlineKeyboardButton(text='На главную', callback_data='back_start')
    )

    msg_text = 'Список доступных мероприятий:'
    return (
        await message.answer(msg_text, reply_markup=keyboard.as_markup())
        if isinstance(message, Message)
        else message.message.answer(
            msg_text,
            reply_markup=keyboard.as_markup()
        )
    )


@router.callback_query(Text(startswith='events_'))
async def get_entry(callback: CallbackQuery, state: FSMContext):
    event_id = int(callback.data.split('_')[1])
    headers = await get_headers(state)
    response = await make_get_request(
        config.base_endpoint + f'events/{event_id}/',
        headers=headers
    )

    msg_text = (
        f'*{response.get("name")}*\n\n'
        f'{response.get("text")}\n\n'
        f'*Сроки проведения: '
        f'{format_date(response.get("start_time"))} - '
        f'{format_date(response.get("end_time"))}*\n\n'
        f'_Автор: {response.get("author").get("first_name")} '
        f'{response.get("author").get("last_name")}_'
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Назад', callback_data='back_events')]
        ]
    )

    await callback.message.delete()
    await callback.message.answer(
        msg_text,
        parse_mode='Markdown',
        reply_markup=keyboard
    )
