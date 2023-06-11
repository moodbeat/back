from datetime import date

from django.core.exceptions import ValidationError


def validate_results(value):

    if not isinstance(value, list):
        raise ValidationError('Значение должно быть списком.')

    if len(value) != 8:
        raise ValidationError('Список должен содержать 8 элементов.')

    for num in value:
        if not isinstance(num, int) or num < 1 or num > 10:
            raise ValidationError(
                'Элементы списка должны быть целыми числами в диапазоне '
                'от 1 до 10.'
            )


def validate_completed_survey(
    survey: int,
    questions: list,
    results: list,
    employee: object,
    completed_survey: object
):

    if not isinstance(questions, list) or not isinstance(results, list):
        raise ValidationError('Значение должно быть списком.')

    if not len(questions) == len(results):
        raise ValidationError(
            'Количество значений в обоих списках должно быть равным.'
        )

    for num in questions:
        if not isinstance(num, int) or num < 1:
            raise ValidationError(
                'Элементы списка должны быть целыми числами.'
            )

    for num in results:
        if not isinstance(num, int):
            raise ValidationError('Элементы списка должны быть числами.')

    if survey.questions.count() != len(questions):
        raise ValidationError(
            'Количество предоставленных id вопросов в списке не соответствует '
            'их количеству в данном опросе.'
        )

    filter_params = {
        'employee': employee,
        'survey': survey,
        'next_attempt_date__gt': date.today(),
    }
    if completed_survey.objects.filter(**filter_params).exists():
        raise ValidationError(
            'Слишком рано для повторного прохождения опроса.'
        )
