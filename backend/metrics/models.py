from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import (MaxValueValidator, MinLengthValidator,
                                    MinValueValidator)
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from users.models import Department, MentalState

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
    for_all = models.BooleanField(
        verbose_name='Доступен всем',
        help_text=(
            'При положительном значении, поле с отделами игнорируется  '
            'и уведомления о появлении нового опроса отправляются всем '
            'активным сотрудникам'
        ),
        default=True
    )
    department = models.ManyToManyField(
        Department,
        verbose_name='Отделы',
        blank=True
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
    text = models.TextField(
        verbose_name='Текст после прохождения опроса',
        blank=True,
        null=True
    )
    frequency = models.PositiveSmallIntegerField(
        verbose_name='Периодичность прохождения опроса',
        default=30,
        validators=[MaxValueValidator(90)],
    )
    min_range = models.PositiveSmallIntegerField(
        verbose_name='Минимальный средний порог расчета',
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        null=True
    )
    max_range = models.PositiveSmallIntegerField(
        verbose_name='Максимальный средний порог расчета',
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        null=True
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

    def clean(self):

        if self.min_range is not None or self.max_range is not None:

            if self.min_range is None or self.max_range is None:
                raise ValidationError(
                    'Должны быть заполнены нижний и максимальный пороги вместе'
                    ', либо ни один из них.'
                )

            if self.min_range > self.max_range:
                raise ValidationError(
                    'Минимальное значение не может быть больше максимального '
                    'значения.'
                )

            if self.max_range < self.min_range:
                raise ValidationError(
                    'Максимальное значение не может быть меньше минимального '
                    'значения.'
                )

        return super().clean()


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
    key = models.IntegerField(
        verbose_name='Ключ',
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
    mental_state = models.ForeignKey(
        MentalState,
        verbose_name='Оценка состояния',
        on_delete=models.SET_NULL,
        null=True
    )
    summary = models.JSONField(
        verbose_name='Сводка',
        null=True,
        default=None
    )
    results = models.JSONField(
        verbose_name='Результаты'
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

    def set_mental_state(self, result_in_persent):

        level = 1

        if self.survey.min_range is not None:

            if result_in_persent in range(self.survey.min_range):
                level = 1
            elif result_in_persent in range(
                self.survey.min_range, self.survey.max_range
            ):
                level = 2
            elif result_in_persent in range(self.survey.max_range, 101):
                level = 3

        mental_state = MentalState.objects.filter(level=level).first()
        self.mental_state = mental_state
        self.employee.mental_state = mental_state
        self.employee.save()
