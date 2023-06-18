from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_event_data(start_time, end_time):
    if start_time and end_time:

        if start_time >= end_time:
            raise ValidationError(
                'Дата и время начала должны быть раньше даты и времени '
                'окончания.'
            )

        current_time = timezone.localtime()
        if start_time <= current_time:
            raise ValidationError(
                'Дата и время начала должна быть не раньше текущего времени.'
            )

        time_difference = end_time - start_time
        if (
            time_difference.total_seconds() < 1800
            or time_difference.total_seconds() > 43200
        ):
            raise ValidationError(
                'Разница между датой и временем начала и окончания должна '
                'быть от 30 минут до 12 часов.'
            )
