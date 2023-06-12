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
    results: list,
    employee: object,
    completed_survey: object,
    variant: object
):
    # переделать это все по человечески
    questions = [item['question_id'] for item in results]
    values = [item['variant_value'] for item in results]

    for num in questions:
        if not isinstance(num, int) or num < 1:
            raise ValidationError(
                'Элементы списка должны быть целыми положительными числами.'
            )

    for num in values:
        if not isinstance(num, int):
            raise ValidationError('Элементы списка должны быть числами.')

    if len(set(questions)) != len(questions):
        raise ValidationError('id в списке вопросов не должны повторяться.')

    if survey.questions.count() != len(questions):
        raise ValidationError(
            'Количество предоставленных id вопросов в списке не соответствует '
            'их количеству в данном опросе.'
        )

    question_ids = list(survey.questions.values_list('id', flat=True))

    if set(questions) != set(question_ids):
        missing_ids = set(questions) - set(question_ids)
        raise ValidationError(
            'Предоставленные id вопросов '
            f'{list(missing_ids)} не содержатся в данном опросе.'
        )

    variants_values = set(
        variant.objects
        .filter(survey_type=survey.type)
        .values_list('value', flat=True)
    )

    for value in list(set(values)):
        if value not in variants_values:
            raise ValidationError(
                f'Недопустимое значение {value} в variant_value. '
                'В данном опросе допустимы следующие значения: '
                f'{list(variants_values)}'
            )

    filter_params = {
        'employee': employee,
        'survey': survey,
        'next_attempt_date__gt': date.today(),
    }
    if (
        survey.frequency
        and completed_survey.objects.filter(**filter_params).exists()
    ):
        raise ValidationError(
            'Слишком рано для повторного прохождения опроса.'
        )
