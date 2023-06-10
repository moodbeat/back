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
