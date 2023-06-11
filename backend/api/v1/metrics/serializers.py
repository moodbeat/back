from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import serializers

from metrics.models import (Condition, LifeDirection, Question, Survey,
                            UserLifeBalance, Variant)

User = get_user_model()


class ConditionReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Condition
        fields = '__all__'


class ConditionWriteSerializer(serializers.ModelSerializer):

    employee = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Condition
        fields = ('employee', 'mood', 'note', 'date')

    def validate(self, attrs):
        current_time = timezone.localtime()
        user = self.context.get('request', None).user
        last_add_condition = (
            Condition.objects
            .filter(employee=user)
            .order_by('-date')
            .first()
        )
        infinity_freq = self.context.get(
            'request').query_params.get('infinity_freq')
        if last_add_condition and not infinity_freq:
            last_add_date = last_add_condition.date
            if last_add_date and (
                    current_time - last_add_date).total_seconds() < 36000:
                raise ValidationError(
                    'Можно добавлять значения не чаще, чем раз в 10 часов.'
                )
        return attrs

    def to_representation(self, instance):
        return ConditionReadSerializer(instance, context=self.context).data


class LifeDirectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = LifeDirection
        exclude = ('id',)


class LifeBalanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserLifeBalance
        fields = '__all__'


class LifeBalanceCreateSerializer(serializers.ModelSerializer):

    employee = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = UserLifeBalance
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    """Сериализатор для вопросов."""

    class Meta:
        model = Question
        exclude = ('survey', 'mark', 'priority',)


class VariantSerializer(serializers.ModelSerializer):
    """Сериализатор для представления вариантов ответа."""

    class Meta:
        model = Variant
        fields = ('text', 'value')


class UserShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name',)


class SurveySerializer(serializers.ModelSerializer):
    """Сериализатор для представления опроса."""

    author = UserShortSerializer()
    questions = serializers.SerializerMethodField()
    type = serializers.SlugRelatedField(slug_field='slug', read_only=True)
    variants = serializers.SerializerMethodField()
    questions_quantity = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = (
            'id', 'title', 'type', 'frequency', 'creation_date',
            'questions_quantity', 'is_active', 'description', 'author',
            'variants', 'questions'
        )

    def get_questions_quantity(self, obj):
        questions = obj.questions.all()
        return questions.count()

    def get_questions(self, obj):
        questions = obj.questions.all()

        if questions:
            question_data = []
            for index, question in enumerate(questions, start=1):
                question_dict = QuestionSerializer(question).data
                question_dict['number'] = index
                question_data.append(question_dict)
            return question_data

        return None

    def get_variants(self, obj):
        variants = Variant.objects.filter(survey_type=obj.type)
        serializer = VariantSerializer(variants, many=True)
        return serializer.data

# class SurveyCreateSerializer(serializers.ModelSerializer):
#     """Сериализатор для создания опроса."""

#     author = serializers.HiddenField(
#         default=serializers.CurrentUserDefault(),
#     )
#     questions = QuestionSerializer(many=True)
#     department = serializers.PrimaryKeyRelatedField(
#         queryset=Department.objects.all(),
#         many=True,
#     )

#     class Meta:
#         model = Survey
#         exclude = ('creation_date',)

#     def to_representation(self, instance):
#         """После создания объект сериализуется через `SurveySerializer`."""
#         return SurveySerializer(instance, context=self.context).data


# class CompletedSurveySerializer(serializers.ModelSerializer):
#     """Сериализатор для представления результатов пройденных опросов."""

#     class Meta:
#         model = CompletedSurvey
#         exclude = ('positive_value', 'negative_value',)


# class CompletedSurveyCreateSerializer(serializers.ModelSerializer):
#     """Сериализатор для записи результатов прохождения опроса."""

#     employee = serializers.HiddenField(
#         default=serializers.CurrentUserDefault(),
#     )
#     completion_date = serializers.HiddenField(
#         default=date.today,
#     )

#     class Meta:
#         model = CompletedSurvey
#         exclude = ('result', 'next_attempt_date',)

#     def validate(self, data):
#         if (
#             data['positive_value'] + data['negative_value']
#         ) != data['survey'].questions.count():
#             raise serializers.ValidationError(
#                 'Количество ответов не соответстует количеству вопросов'
#             )
#         filter_params = {
#             'employee': data['employee'],
#             'survey': data['survey'],
#             'next_attempt_date__gt': date.today(),
#         }
#         if (
#             data['survey'].frequency
#             and models.CompletedSurvey.objects.filter(
#                 **filter_params).exists()
#         ):
#             raise ValidationError(
#                 'Слишком рано для повторного прохождения опроса'
#             )
#         return data

#     def to_representation(self, instance):
#         """После создания сериализуется через `CompletedSurveySerializer`."""
#         return CompletedSurveySerializer(instance, context=self.context).data
