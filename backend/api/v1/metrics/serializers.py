# from datetime import timedelta
from datetime import date

from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import serializers

from metrics import models
from users.models import Department


class ConditionReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Condition
        fields = ('mood', 'note', 'date')


class ConditionWriteSerializer(serializers.ModelSerializer):
    mood = serializers.ChoiceField(
        choices=models.Condition.ENERGY_MOOD_CHOICES
    )
    employee = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    date = serializers.SerializerMethodField()

    def get_date(self, obj):
        return timezone.localtime()

    class Meta:
        model = models.Condition
        fields = ('employee', 'mood', 'note', 'date')

    # не получается вылидировать поле
    # def validate_date(self, value):
    #     current_time = timezone.localtime()
    #     last_add_date = Condition.objects.filter().order_by('-date').first()
    #     if last_add_date and (current_time - last_add_date).hour < 10:
    #         raise ValidationError(
    #             'Можно добавлять значения не чаще, чем раз в сутки!')
    #     return value


class QuestionSerializer(serializers.ModelSerializer):
    """Сериализатор для вопросов."""

    class Meta:
        model = models.Question
        fields = ('text',)


class SurveySerializer(serializers.ModelSerializer):
    """Сериализатор для представления опроса."""

    questions = QuestionSerializer(many=True)

    class Meta:
        model = models.Survey
        fields = '__all__'


class SurveyCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания опроса."""

    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )
    questions = QuestionSerializer(many=True)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        many=True,
    )

    class Meta:
        model = models.Survey
        exclude = ('creation_date',)

    def to_representation(self, instance):
        """После создания объект сериализуется через `SurveySerializer`."""
        return SurveySerializer(instance, context=self.context).data


class CompletedSurveySerializer(serializers.ModelSerializer):
    """Сериализатор для представления результатов пройденных опросов."""

    class Meta:
        model = models.CompletedSurvey
        exclude = ('positive_value', 'negative_value',)


class CompletedSurveyCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для записи результатов прохождения опроса."""

    employee = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )
    completion_date = serializers.HiddenField(
        default=date.today,
    )

    class Meta:
        model = models.CompletedSurvey
        exclude = ('result', 'next_attempt_date',)

    def validate(self, data):
        if (
            data['positive_value'] + data['negative_value']
        ) != data['survey'].questions.count():
            raise serializers.ValidationError(
                'Количество ответов не соответстует количеству вопросов'
            )
        filter_params = {
            'employee': data['employee'],
            'survey': data['survey'],
            'next_attempt_date__gt': date.today(),
        }
        if models.CompletedSurvey.objects.filter(**filter_params).exists():
            raise ValidationError(
                'Слишком рано для повторного прохождения опроса'
            )
        return data

    def to_representation(self, instance):
        """После создания сериализуется через `CompletedSurveySerializer`."""
        return CompletedSurveySerializer(instance, context=self.context).data