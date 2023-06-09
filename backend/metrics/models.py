from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import (MaxValueValidator, MinLengthValidator,
                                    MinValueValidator)
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from users.models import Department, MentalState

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

    set1 = models.PositiveSmallIntegerField(
        verbose_name='Показатели жизненного направления под номером 1',
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ],
        default=1
    )
    set2 = models.PositiveSmallIntegerField(
        verbose_name='Показатели жизненного направления под номером 2',
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ],
        default=1
    )
    set3 = models.PositiveSmallIntegerField(
        verbose_name='Показатели жизненного направления под номером 3',
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ],
        default=1
    )
    set4 = models.PositiveSmallIntegerField(
        verbose_name='Показатели жизненного направления под номером 4',
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ],
        default=1
    )
    set5 = models.PositiveSmallIntegerField(
        verbose_name='Показатели жизненного направления под номером 5',
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ],
        default=1
    )
    set6 = models.PositiveSmallIntegerField(
        verbose_name='Показатели жизненного направления под номером 6',
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ],
        default=1
    )
    set7 = models.PositiveSmallIntegerField(
        verbose_name='Показатели жизненного направления под номером 7',
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ],
        default=1
    )
    set8 = models.PositiveSmallIntegerField(
        verbose_name='Показатели жизненного направления под номером 8',
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ],
        default=1
    )

    class Meta:
        ordering = ('-date',)
        verbose_name = 'Жизненный баланс сотрудника'
        verbose_name_plural = 'Жизненный баланс сотрудников'


class Survey(models.Model):
    """Опрос."""

    author = models.ForeignKey(
        User,
        verbose_name='автор опроса',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    department = models.ManyToManyField(
        Department,
        through='SurveyDepartment',
        verbose_name='отдел',
    )
    title = models.CharField(
        verbose_name='название опроса',
        max_length=255,
    )
    description = models.CharField(
        verbose_name='описание опроса',
        blank=True,
        null=True,
        max_length=255,
    )
    frequency = models.PositiveSmallIntegerField(
        verbose_name='периодичность прохождения опроса',
        default=30,
        validators=[MaxValueValidator(90)],
    )
    creation_date = models.DateTimeField(
        verbose_name='дата и время создания опроса',
        default=timezone.now,
    )
    is_active = models.BooleanField(
        verbose_name='статус активности',
        default=True,
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'опрос'
        verbose_name_plural = 'опросы'

    def __str__(self):
        return self.title


class SurveyDepartment(models.Model):
    """Модель для связи департаментов и опросов."""

    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        verbose_name='опрос',
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        verbose_name='департамент',
    )


class Question(models.Model):
    """Вопрос к опросу."""

    survey = models.ForeignKey(
        Survey,
        verbose_name='опрос',
        on_delete=models.CASCADE,
        related_name='questions',
    )
    text = models.CharField(
        verbose_name='текст вопроса',
        max_length=400,
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'вопрос'
        verbose_name_plural = 'вопросы'

    def __str__(self):
        return self.text


class CompletedSurvey(models.Model):
    """Модель связывающая сотрудников и их результаты прохождения опроса."""

    class ResultInterpretation(models.TextChoices):
        NORM = 'Нормальное'
        HARD = 'Тревожное'
        CRIT = 'В группе риска'

    employee = models.ForeignKey(
        User,
        verbose_name='сотрудник',
        on_delete=models.CASCADE,
        related_name='results',
    )
    survey = models.ForeignKey(
        Survey,
        verbose_name='опрос',
        on_delete=models.CASCADE,
    )
    result = models.TextField(
        verbose_name='интерпретация результата',
        choices=ResultInterpretation.choices,
        blank=True,
    )
    positive_value = models.PositiveSmallIntegerField(
        verbose_name='кол-во утвердительных ответов',
        validators=[MaxValueValidator(100)],
    )
    negative_value = models.PositiveSmallIntegerField(
        verbose_name='кол-во отрицательных ответов',
        validators=[MaxValueValidator(100)],
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
        verbose_name = 'результат опроса сотрудника'
        verbose_name_plural = 'результаты опросов сотрудников'

    def __str__(self):
        return (f'"{self.survey.title}" пройден '
                f'сотрудником {self.employee.get_full_name}')

    def clean(self):
        """Дополнительная валидация перед сохранением."""
        if (
            self.positive_value + self.negative_value
        ) != self.survey.questions.count():
            raise ValidationError(
                'Количество ответов не соответстует количеству вопросов'
            )
        filter_params = {
            'employee': self.employee,
            'survey': self.survey,
            'next_attempt_date__gt': date.today(),
        }
        if CompletedSurvey.objects.filter(**filter_params).exists():
            raise ValidationError(
                'Слишком рано для повторного прохождения опроса'
            )
        return super().clean()

    def save(self, *args, **kwargs):
        """При создании объекта интерпретирует значение результата в текст.

        Также в зависимости от периодичности `frequency`, установленной
        в модели `Survey` определяет дату следующей попытки прохождения опроса.
        """
        result_in_persent = (
            self.positive_value / self.survey.questions.count() * 100
        )
        if result_in_persent in range(11):
            state = self.ResultInterpretation.NORM
            level = 1
        elif result_in_persent in range(11, 69):
            state = self.ResultInterpretation.HARD
            level = 2
        elif result_in_persent in range(69, 101):
            state = self.ResultInterpretation.CRIT
            level = 3

        self.result = state

        mental_state = MentalState.objects.filter(level=level).first()
        self.employee.mental_state = mental_state
        self.employee.save()
        self.next_attempt_date = date.today() + timedelta(
            days=self.survey.frequency
        )
        return super(CompletedSurvey, self).save(*args, **kwargs)
