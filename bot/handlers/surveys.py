from aiogram import Router, flags
from aiogram.filters import Text
from aiogram.filters.callback_data import CallbackData
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from middlewares import AuthMiddleware
from services.survey_service import (get_last_ten_surveys, get_survey_by_id,
                                     get_survey_from_storage,
                                     post_survey_result_data_with_return_data,
                                     save_survey_in_storage)
from utils.local_datetime import get_local_datetime_now

router = Router()

router.message.middleware(AuthMiddleware())
router.callback_query.middleware(AuthMiddleware())


class SurveyState(StatesGroup):
    process = State()
    results = State()


class SurveyAnswersCallbackFactory(CallbackData, prefix='answer'):
    question_id: int
    answer_value: int


@router.callback_query(Text(startswith='back_survey'))
@router.message(Command('survey'))
@flags.state_reset
async def cmd_survey(message: Message | CallbackQuery, state: FSMContext):
    if isinstance(message, CallbackQuery):
        await message.message.delete()

    surveys = await get_last_ten_surveys(state)

    if not surveys:
        return await message.answer(
            'На данный момент нет доступных опросов'
        )

    keyboard = InlineKeyboardBuilder()
    for survey in surveys:
        keyboard.row(
            InlineKeyboardButton(
                text=survey.title,
                callback_data=f'survey_{survey.id}'
            )
        )
    keyboard.row(
        InlineKeyboardButton(text='На главную', callback_data='back_start')
    )

    msg_text = 'Список последних опросов:'
    return (
        await message.answer(msg_text, reply_markup=keyboard.as_markup())
        if isinstance(message, Message)
        else await message.message.answer(
            msg_text,
            reply_markup=keyboard.as_markup()
        )
    )


@router.callback_query(Text(startswith='survey_'))
async def get_survey(callback: CallbackQuery, state: FSMContext):
    survey_id = int(callback.data.split('_')[1])
    survey = await get_survey_by_id(survey_id, state)
    await save_survey_in_storage(obj=survey, state=state)

    msg_text = (
        f'*{survey.title}*\n\n'
        f'{survey.description}\n\n'
        f'Периодичность прохождения (в днях): {survey.frequency}\n'
        f'Количество вопросов: {survey.questions_quantity}\n'
        f'*Автор: {survey.author.full_name}*'
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
    await callback.message.answer(
        msg_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )


def answers_keyboard(question_id, answers):
    keyboard = InlineKeyboardBuilder()
    for variant in answers:
        keyboard.button(
            text=variant.text,
            callback_data=SurveyAnswersCallbackFactory(
                question_id=question_id,
                answer_value=variant.value
            )
        )
    keyboard.row(
        InlineKeyboardButton(text='На главную', callback_data='back_start')
    )
    keyboard.adjust(1)
    return keyboard.as_markup()


@router.callback_query(Text(startswith='take_survey_'))
async def take_survey(callback: CallbackQuery, state: FSMContext):
    survey = await get_survey_from_storage(state)
    survey_id = int(callback.data.split('_')[-1])
    if survey.id != survey_id:
        await get_survey(callback, state)
        return

    await state.set_state(SurveyState.process)
    questions_counter = 0
    await state.update_data({
        'results': [],
        'questions_counter': questions_counter
    })

    await callback.message.delete()
    await callback.message.answer(
        survey.questions[questions_counter].text,
        reply_markup=answers_keyboard(
            survey.questions[questions_counter].id,
            survey.variants
        )
    )


@router.callback_query(
    SurveyState.process, SurveyAnswersCallbackFactory.filter()
)
async def process_survey(
    callback: CallbackQuery,
    state: FSMContext,
    callback_data: SurveyAnswersCallbackFactory
):
    user_data = await state.get_data()
    user_data['results'].append({
        'question_id': callback_data.question_id,
        'variant_value': callback_data.answer_value
    })

    user_data['questions_counter'] += 1
    questions_counter = user_data['questions_counter']
    await state.set_data(user_data)
    survey = await get_survey_from_storage(state)

    if questions_counter < survey.questions_quantity:
        await callback.message.edit_text(
            survey.questions[questions_counter].text,
            reply_markup=answers_keyboard(
                survey.questions[questions_counter].id,
                survey.variants
            )
        )
        return
    await state.set_state(SurveyState.results)
    await callback.message.delete()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Назад', callback_data='back_survey'
                ),
                InlineKeyboardButton(
                    text='Отправить',
                    callback_data='post_results'
                )
            ]
        ]
    )
    await callback.message.answer(
        text=(
            'Опрос завершен!\nХотите отправить результаты?\n'
            'Или вернуться к выбору теста?'
        ),
        reply_markup=keyboard
    )


@router.callback_query(SurveyState.results, Text(startswith='post_results'))
async def needhelp_comment(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    user_data.pop('questions_counter')
    data = {
        'survey': user_data.pop('survey')['id'],
        'results': user_data.pop('results')
    }
    await state.set_data(user_data)

    result = await post_survey_result_data_with_return_data(data, state)
    mental_state = result.mental_state
    await callback.message.delete()

    message_text = (
        'Ваши результаты пройденного опроса '
        f'*{result.survey.title}*:\n\n'
        f'{mental_state.message}'
    )
    if result.next_attempt_date > get_local_datetime_now().date():
        message_text += f'\nДата следующей попытки: {result.next_attempt_date}'
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Назад', callback_data='back_survey'
                ),
                InlineKeyboardButton(
                    text='На главную', callback_data='back_start'
                )
            ]
        ]
    )
    await callback.message.answer(
        text=message_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )
    await state.set_state(state=None)
