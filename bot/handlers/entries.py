from aiogram import Router, flags
from aiogram.filters import Text
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message, URLInputFile)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from middlewares import AuthMiddleware
from services.entry_service import get_entry_by_id, get_last_ten_entries

router = Router()

router.message.middleware(AuthMiddleware())
router.callback_query.middleware(AuthMiddleware())


@router.callback_query(Text(startswith='back_entries'))
@router.message(Command('entries'))
@flags.state_reset
async def cmd_entries(message: Message | CallbackQuery, state: FSMContext):
    if isinstance(message, CallbackQuery):
        await message.message.delete()

    entries = await get_last_ten_entries(state)

    if not entries:
        return await message.answer('На данный момент нет доступных статей.')

    keyboard = InlineKeyboardBuilder()
    for entry in entries:
        keyboard.row(
            InlineKeyboardButton(
                text=entry.title,
                callback_data=f'entries_{entry.id}'
            )
        )
    keyboard.row(
        InlineKeyboardButton(text='На главную', callback_data='back_start')
    )
    msg_text = 'Список последних статей:'
    return (
        await message.answer(msg_text, reply_markup=keyboard.as_markup())
        if isinstance(message, Message)
        else await message.message.answer(
            msg_text,
            reply_markup=keyboard.as_markup()
        )
    )


@router.callback_query(Text(startswith='entries_'))
async def get_entry(callback: CallbackQuery, state: FSMContext):
    entry_id = int(callback.data.split('_')[1])
    entry = await get_entry_by_id(entry_id, state)

    if entry.url:
        body = entry.url
    else:
        body = entry.text
    msg_text = (
        f'*{entry.title}*\n\n'
        f'{body}\n\n'
        f'*Автор: {entry.author.full_name}*'
    )
    if len(msg_text) > 1024:
        msg_text = (
            f'*{entry.title}*\n\n'
            f'{body[:600]}...\n'
            f'[Полный текст статьи]({entry.entry_url})\n\n'
            f'*Автор: {entry.author.full_name}*'
        )

    photo = URLInputFile(
        entry.preview_image,
        filename=f'entries_{entry_id}'
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Назад', callback_data='back_entries')]
        ]
    )

    await callback.message.delete()
    await callback.message.answer_photo(
        photo=photo,
        caption=msg_text,
        parse_mode='Markdown',
        reply_markup=keyboard
    )
