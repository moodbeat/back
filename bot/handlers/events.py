from aiogram import Router, flags
from aiogram.filters import Text
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from middlewares import AuthMiddleware
from services.event_service import get_event_by_id, get_events

router = Router()

router.message.middleware(AuthMiddleware())
router.callback_query.middleware(AuthMiddleware())


@router.callback_query(Text(startswith='back_events'))
@router.message(Command('events'))
@flags.state_reset
async def cmd_events(message: Message | CallbackQuery, state: FSMContext):
    if isinstance(message, CallbackQuery):
        await message.message.delete()

    events = await get_events(state)

    if not events:
        return await message.answer(
            'На данный момент нет доступных мероприятий'
        )

    keyboard = InlineKeyboardBuilder()
    for event in events:
        keyboard.row(
            InlineKeyboardButton(
                text=event.name,
                callback_data=f'events_{event.id}'
            )
        )
    keyboard.row(
        InlineKeyboardButton(text='На главную', callback_data='back_start')
    )

    msg_text = 'Список доступных мероприятий:'
    return (
        await message.answer(msg_text, reply_markup=keyboard.as_markup())
        if isinstance(message, Message)
        else await message.message.answer(
            msg_text,
            reply_markup=keyboard.as_markup()
        )
    )


@router.callback_query(Text(startswith='events_'))
async def get_event(callback: CallbackQuery, state: FSMContext):
    event_id = int(callback.data.split('_')[1])
    event = await get_event_by_id(event_id, state)

    msg_text = (
        f'*{event.name}*\n\n'
        f'{event.text}\n\n'
        f'*Сроки проведения: '
        f'{event.start_time.strftime("%d.%m.%Y %H:%M")} - '
        f'{event.end_time.strftime("%d.%m.%Y %H:%M")}*\n\n'
        f'_Автор: {event.author.full_name}_'
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
