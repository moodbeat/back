from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import (MaxValueValidator, MinLengthValidator,
                                    MinValueValidator)
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from users.models import Department

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
        NORM = 'Нормальное состояние'
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
            mental_state = self.ResultInterpretation.NORM
        elif result_in_persent in range(11, 69):
            mental_state = self.ResultInterpretation.HARD
        elif result_in_persent in range(69, 101):
            mental_state = self.ResultInterpretation.CRIT

        self.result = mental_state
        self.employee.mental_state = mental_state
        self.employee.save()
        self.next_attempt_date = date.today() + timedelta(
            days=self.survey.frequency
        )
        return super(CompletedSurvey, self).save(*args, **kwargs)
