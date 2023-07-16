from __future__ import annotations

from aiogram import Router
from aiogram.filters import Text
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from middlewares.auth import AuthMiddleware
from services.need_help_service import (get_help_types_by_specialist_id,
                                        get_specialists, post_need_help_data)
from services.user_service import get_current_user

router = Router()

router.message.middleware(AuthMiddleware())


class HelpState(StatesGroup):
    recipient = State()
    type = State()
    comment = State()


@router.message(Command('need_help'))
async def cmd_needhelp(message: Message, state: FSMContext):
    user = await get_current_user(state)
    msg_text = (
        f'Привет, {user.first_name}!\n'
        'Выберите, кому хотите направить обращение.'
    )
    specialists = await get_specialists(state)

    keyboard = InlineKeyboardBuilder()
    for specialist in specialists:
        text = (
            f'{specialist.role}, '
            f'{specialist.full_name}'
        )
        keyboard.row(
            InlineKeyboardButton(
                text=text,
                callback_data=f'recipient_{specialist.id}'
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

    help_types = await get_help_types_by_specialist_id(recipient_id, state)
    msg_text = 'А теперь выберите тип обращения'
    keyboard = InlineKeyboardBuilder()
    for help_type in help_types:
        text = help_type.title
        keyboard.row(
            InlineKeyboardButton(
                text=text,
                callback_data=f'type_{help_type.id}'
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

    msg_text = 'А теперь опишите проблему'
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

    await post_need_help_data(user_data, state)
    await message.answer('Обращение сформировано и отправлено')
    await state.set_state(state=None)
