from datetime import date

from django.contrib.auth import get_user_model
from django.core.validators import (MaxValueValidator, MinLengthValidator,
                                    MinValueValidator)
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from users.models import Department

from .validators import validate_results

User = get_user_model()


class Condition(models.Model):

    employee = models.ForeignKey(
        User,
        verbose_name='Сотрудник',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    mood = models.PositiveSmallIntegerField(
        verbose_name='Настроение',
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    note = models.CharField(
        verbose_name='Заметка',
        max_length=128,
        null=True,
        blank=True,
        validators=[MinLengthValidator(4)]
    )
    date = models.DateTimeField(
        verbose_name=_('Дата/время добавления показателей'),
        default=timezone.now
    )

    class Meta:
        verbose_name = 'Состояние (сотрудника)'
        verbose_name_plural = 'Состояния'
        ordering = ('-date',)

    def __str__(self):
        return (
            'Состояние сотрудника '
            f'{self.employee}: {self.mood} ({self.date})'
        )


class LifeDirection(models.Model):
    """Жизненное направление для колеса баланса."""

    name = models.CharField(
        verbose_name='Наименование',
        max_length=128,
    )
    num = models.PositiveSmallIntegerField(
        verbose_name='Номер',
        unique=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(8)
        ]
    )
    description = models.TextField(
        verbose_name='Описание',
        max_length=256,
        blank=True,
        null=True
    )

    class Meta:
        ordering = ('num',)
        verbose_name = 'Жизненное направление'
        verbose_name_plural = 'Жизненные направления'

    def __str__(self):
        return self.name


class UserLifeBalance(models.Model):
    """Оценка/установка баланса."""

    employee = models.ForeignKey(
        User,
        verbose_name='Сотрудник',
        related_name='life_balance',
        on_delete=models.CASCADE
    )
    date = models.DateTimeField(
        verbose_name='Дата/время добавления показателей',
        default=timezone.now
    )
    set_priority = models.BooleanField(
        verbose_name='Задать новые приоритеты.',
        default=False
    )
    results = models.JSONField(
        verbose_name='Результаты',
        validators=[validate_results]
    )

    class Meta:
        ordering = ('-date',)
        verbose_name = 'Жизненный баланс сотрудника'
        verbose_name_plural = 'Жизненный баланс сотрудников'


class SurveyType(models.Model):
    """Тип опроса."""

    name = models.CharField(
        verbose_name='Наименование',
        max_length=255
    )
    slug = models.SlugField(
        verbose_name='Slug'
    )
    description = models.TextField(
        verbose_name='Описание',
        max_length=255,
        blank=True,
        null=False
    )

    class Meta:
        verbose_name = 'Тип опросов'
        verbose_name_plural = 'Типы опросов'

    def __str__(self):
        return self.slug


class Survey(models.Model):
    """Опрос."""

    author = models.ForeignKey(
        User,
        verbose_name='Автор опроса',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    department = models.ManyToManyField(
        Department,
        verbose_name='Отделы',
    )
    title = models.CharField(
        verbose_name='Название опроса',
        max_length=255,
    )
    type = models.ForeignKey(
        SurveyType,
        verbose_name='Тип опроса',
        on_delete=models.SET_NULL,
        null=True
    )
    description = models.TextField(
        verbose_name='Описание опроса',
        blank=True,
        null=True,
        max_length=800,
    )
    frequency = models.PositiveSmallIntegerField(
        verbose_name='Периодичность прохождения опроса',
        default=30,
        validators=[MaxValueValidator(90)],
    )
    creation_date = models.DateTimeField(
        verbose_name='Дата и время создания опроса',
        default=timezone.now,
    )
    is_active = models.BooleanField(
        verbose_name='Статус активности',
        default=True,
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Опрос'
        verbose_name_plural = 'Опросы'

    def __str__(self):
        return self.title


class Question(models.Model):
    """Вопрос к опросу."""

    survey = models.ForeignKey(
        Survey,
        verbose_name='Опрос',
        on_delete=models.CASCADE,
        related_name='questions',
    )
    text = models.TextField(
        verbose_name='Текст вопроса',
        max_length=800,
    )
    mark = models.IntegerField(
        verbose_name='Метка',
        null=True,
        blank=True
    )
    priority = models.PositiveSmallIntegerField(
        verbose_name='Приоритет при выдаче',
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(99)
        ]
    )

    class Meta:
        ordering = ('priority', 'id')
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return self.text


class Variant(models.Model):
    """Вариант ответа."""

    text = models.CharField(
        verbose_name='Текст варианта',
        max_length=255
    )
    priority = models.PositiveSmallIntegerField(
        verbose_name='Приоритет при выдаче',
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(99)
        ]
    )
    survey_type = models.ForeignKey(
        SurveyType,
        verbose_name='Тип опроса',
        on_delete=models.SET_NULL,
        null=True
    )
    value = models.IntegerField(
        verbose_name='Значение',
        null=True,
        blank=True
    )

    class Meta:
        ordering = ('priority', 'id')
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответа'

    def __str__(self):
        return self.text


class CompletedSurvey(models.Model):
    """Модель связывающая сотрудников и их результаты прохождения опроса."""

    employee = models.ForeignKey(
        User,
        verbose_name='сотрудник',
        on_delete=models.CASCADE,
        related_name='survey_results',
    )
    survey = models.ForeignKey(
        Survey,
        verbose_name='опрос',
        on_delete=models.CASCADE,
    )
    summary = models.JSONField(
        verbose_name='Сводка'
    )
    questions = models.JSONField(
        verbose_name='Вопросы',
        null=True,
        default=None
    )
    results = models.JSONField(
        verbose_name='Выбранные варианты'
    )
    completion_date = models.DateField(
        verbose_name='дата прохождения опроса',
        default=date.today,
    )
    next_attempt_date = models.DateField(
        verbose_name='дата следующей попытки',
        default=date.today,
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Результат опроса сотрудника'
        verbose_name_plural = 'Результаты опросов сотрудников'

    def __str__(self):
        return (f'"{self.survey.title}" Пройден '
                f'сотрудником {self.employee.get_full_name}')

    # def clean(self):
    #     """Дополнительная валидация перед сохранением."""
    #     if (
    #         self.positive_value + self.negative_value
    #     ) != self.survey.questions.count():
    #         raise ValidationError(
    #             'Количество ответов не соответстует количеству вопросов'
    #         )
    #     filter_params = {
    #         'employee': self.employee,
    #         'survey': self.survey,
    #         'next_attempt_date__gt': date.today(),
    #     }
    #     if CompletedSurvey.objects.filter(**filter_params).exists():
    #         raise ValidationError(
    #             'Слишком рано для повторного прохождения опроса'
    #         )
    #     return super().clean()

    # def save(self, *args, **kwargs):
    #     """При создании объекта интерпретирует значение результата в текст.

    #     Также в зависимости от периодичности `frequency`, установленной
    #     в модели `Survey` определяет дату следующей попытки прохождения
    #     опроса.
    #     """
    #     result_in_persent = (
    #         self.positive_value / self.survey.questions.count() * 100
    #     )
    #     if result_in_persent in range(11):
    #         state = self.ResultInterpretation.NORM
    #         level = 1
    #     elif result_in_persent in range(11, 69):
    #         state = self.ResultInterpretation.HARD
    #         level = 2
    #     elif result_in_persent in range(69, 101):
    #         state = self.ResultInterpretation.CRIT
    #         level = 3

    #     self.result = state

    #     mental_state = MentalState.objects.filter(level=level).first()
    #     self.employee.mental_state = mental_state
    #     self.employee.save()
    #     self.next_attempt_date = date.today() + timedelta(
    #         days=self.survey.frequency
    #     )
    #     return super(CompletedSurvey, self).save(*args, **kwargs)
