from aiogram import Router, flags
from aiogram.filters import Text
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from middlewares import AuthMiddleware
from services.hot_line_service import (get_help_types_by_specialist_id,
                                       get_specialists, post_hot_line_data)
from services.user_service import get_current_user

router = Router()

router.message.middleware(AuthMiddleware())


class HotLineState(StatesGroup):
    recipient = State()
    type = State()
    comment = State()


@flags.state_reset
@router.message(Command('hot_line'))
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
    await state.update_data(hot_line=dict())
    await state.set_state(HotLineState.recipient)
    await message.answer(
        msg_text,
        reply_markup=keyboard.as_markup()
    )


@router.callback_query(Text(startswith='recipient_'))
@router.message(HotLineState.recipient)
async def needhelp_recipient(callback: CallbackQuery, state: FSMContext):
    recipient_id = int(callback.data.split('_')[1])
    user_data = await state.get_data()
    user_data['hot_line'].update(recipient=recipient_id)
    await state.set_data(user_data)
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

    await state.set_state(HotLineState.type)
    await callback.message.answer(
        msg_text,
        reply_markup=keyboard.as_markup()
    )


@router.callback_query(Text(startswith='type_'))
@router.message(HotLineState.type)
async def needhelp_type(callback: CallbackQuery, state: FSMContext):
    type_id = int(callback.data.split('_')[1])
    user_data = await state.get_data()
    user_data['hot_line'].update(type=type_id)
    await state.set_data(user_data)
    await callback.message.delete()

    msg_text = 'А теперь опишите проблему'
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text='На главную', callback_data='back_start')
    )
    await state.set_state(HotLineState.comment)
    await callback.message.answer(
        msg_text,
        reply_markup=keyboard.as_markup()
    )


@router.message(HotLineState.comment)
async def needhelp_comment(message: Message, state: FSMContext):
    user_data = await state.get_data()
    user_data['hot_line'].update(comment=message.text)

    await post_hot_line_data(user_data['hot_line'], state)
    await message.answer('Обращение сформировано и отправлено')
    await state.set_state(state=None)
