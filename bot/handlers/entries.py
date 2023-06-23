from __future__ import annotations

from aiogram import Router
from aiogram.filters import Text
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    URLInputFile
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config_reader import config
from handlers.api_request import get_headers, make_get_request
from middlewares.auth import AuthMiddleware


router = Router()

router.message.middleware(AuthMiddleware())


@router.callback_query(Text(startswith='back_entries'))
@router.message(Command('entries'))
async def cmd_entries(message: Message | CallbackQuery, state: FSMContext):

    if isinstance(message, CallbackQuery):
        await message.message.delete()

    headers = await get_headers(state)

    response = await make_get_request(
        config.base_endpoint + 'entries/',
        headers=headers
    )

    if response.get('count') == 0:
        return await message.answer('На данный момент нет доступных событий.')

    keyboard = InlineKeyboardBuilder()
    for data in response.get('results'):
        keyboard.row(
            InlineKeyboardButton(
                text=data.get('title'),
                callback_data=f'entries_{data.get("id")}'
            )
        )
    msg_text = 'Список доступных событий:'
    return (await message.answer(msg_text, reply_markup=keyboard.as_markup())
            if isinstance(message, Message)
            else message.message.answer(
        msg_text, reply_markup=keyboard.as_markup()
        )
    )


@router.callback_query(Text(startswith='entries_'))
async def get_entry(callback: CallbackQuery, state: FSMContext):
    entry_id = int(callback.data.split('_')[1])
    headers = await get_headers(state)
    response = await make_get_request(
        config.base_endpoint + f'entries/{entry_id}/',
        headers=headers
    )
    # caption_text = f'{response.get("title")}'
    msg_text = (
        f'{response.get("title")}\n'
        f'{response.get("text")}\n\n'
        f'Автор: {response.get("author").get("first_name")} '
        f'{response.get("author").get("last_name")}'
    )
    photo = URLInputFile(
        response.get('preview_image'),
        filename=f'entries_{entry_id}'
    )
    # TODO обработка исключений на случай если текст статьи слишком длинный - TelegramBadRequest
    # TODO обработка видео

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Назад', callback_data='back_entries')]
        ]
    )

    await callback.message.delete()
    await callback.message.answer_photo(
        photo=photo,
        # caption=caption_text,
        caption=msg_text,
        reply_markup=keyboard
    )
    # await callback.message.answer(msg_text, reply_markup=keyboard)
