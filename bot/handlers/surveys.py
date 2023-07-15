from __future__ import annotations

from aiogram import Router
from aiogram.filters import Text
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config_reader import config
from middlewares.auth import AuthMiddleware
from services.api_request import get_headers, make_get_request

router = Router()

router.message.middleware(AuthMiddleware())


class SurveyState(StatesGroup):
    questions = State()
    answers = State()


@router.callback_query(Text(startswith='back_survey'))
@router.message(Command('survey'))
async def cmd_survey(message: Message | CallbackQuery, state: FSMContext):
    if isinstance(message, CallbackQuery):
        await message.message.delete()

    headers = await get_headers(state)
    response = await make_get_request(
        config.base_endpoint + 'metrics/surveys/',
        headers=headers
    )

    if response.get('count') == 0:
        return await message.answer(
            'На данный момент нет доступных опросов'
        )

    keyboard = InlineKeyboardBuilder()
    for data in response.get('results'):
        keyboard.row(
            InlineKeyboardButton(
                text=data.get('title'),
                callback_data=f'survey_{data.get("id")}'
            )
        )
    keyboard.row(
        InlineKeyboardButton(text='На главную', callback_data='back_start')
    )

    msg_text = 'Список доступных опросов:'
    return (
        await message.answer(msg_text, reply_markup=keyboard.as_markup())
        if isinstance(message, Message)
        else message.message.answer(
            msg_text,
            reply_markup=keyboard.as_markup()
        )
    )


@router.callback_query(Text(startswith='survey_'))
async def get_survey(callback: CallbackQuery, state: FSMContext):
    survey_id = int(callback.data.split('_')[1])
    headers = await get_headers(state)
    response = await make_get_request(
        config.base_endpoint + f'metrics/surveys/{survey_id}/',
        headers=headers
    )

    msg_text = (
        f'{response.get("title")}\n'
        f'{response.get("description")}\n'
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Назад', callback_data='back_survey'
                ),
                InlineKeyboardButton(
                    text='Пройти тест',
                    callback_data=f'take_survey_{survey_id}'
                )
            ]
        ]
    )

    await callback.message.delete()
    await callback.message.answer(msg_text, reply_markup=keyboard)


def survey_keyboard(question_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='Да', callback_data=f'yes_{question_id}'
            )],
            [InlineKeyboardButton(
                text='Нет', callback_data=f'no_{question_id}'
            )],
        ]
    )


@router.callback_query(Text(startswith='take_survey_'))
async def take_survey(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SurveyState.questions)
    survey_id = int(callback.data.split('_')[2])
    headers = await get_headers(state)
    response = await make_get_request(
        config.base_endpoint + f'metrics/surveys/{survey_id}/',
        headers=headers
    )

    questions = response.get('questions')
    questions_data = {i: q['text'] for i, q in enumerate(questions, start=0)}
    await state.update_data(questions=questions_data)
    await state.update_data(answers={})
    current_question_id = 0
    await callback.message.delete()
    await callback.message.answer(
        questions_data[current_question_id],
        reply_markup=survey_keyboard(current_question_id)
    )


@router.callback_query(Text(startswith='yes_'))
@router.callback_query(Text(startswith='no_'))
async def process_survey(callback: CallbackQuery, state: FSMContext):
    selected_answer = callback.data.split('_')[0]
    question_id = int(callback.data.split('_')[1])
    data = await state.get_data()
    data['answers'].update({question_id: selected_answer})

    questions = data['questions']
    current_question_id = list(data['answers'].keys()).index(question_id) + 1
    if current_question_id < len(questions):
        await callback.message.edit_text(
            questions[current_question_id],
            reply_markup=survey_keyboard(current_question_id))
    else:
        await callback.message.delete()
        await callback.message.answer('Вы завершили опрос!')
        await state.clear()
