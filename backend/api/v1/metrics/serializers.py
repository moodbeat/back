from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from metrics.models import Condition


class ConditionReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Condition
        fields = ('mood', 'note', 'date')


class ConditionWriteSerializer(serializers.ModelSerializer):
    mood = serializers.ChoiceField(choices=Condition.ENERGY_MOOD_CHOICES)
    employee = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    date = serializers.SerializerMethodField()

    def get_date(self, obj):
        return timezone.localtime()

    class Meta:
        model = Condition
        fields = ('employee', 'mood', 'note', 'date')

    # не получается вылидировать поле
    # def validate_date(self, value):
    #     current_time = timezone.localtime()
    #     last_add_date = Condition.objects.filter().order_by('-date').first()
    #     if last_add_date and (current_time - last_add_date).hour < 10:
    #         raise ValidationError(
    #             'Можно добавлять значения не чаще, чем раз в сутки!')
    #     return value
