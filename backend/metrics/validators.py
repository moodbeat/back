from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_last_filled_date(value):
    today = timezone.now().date()
    if value and value.date() == today:
        raise ValidationError("Информацию можно заполнять только раз в сутки.")