from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
# from api.v1.metrics.validators import validate_last_filled_date
from users.models import Department

User = get_user_model()


class Condition(models.Model):

    # пока по макету делаю
    ENERGY_MOOD_CHOICES = (
        ('Bad', _('Плохо')),
        ('So so', _('Так себе')),
        ('OK', _('Нормально')),
        ('Fine', _('Хорошо')),
        ('Good', _('Отлично')),
    )

    employee = models.ForeignKey(
        User,
        verbose_name='Сотрудник',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    # опять же по макетам это не нужно
    # energy = models.CharField(
    #     verbose_name='Энергия',
    #     choices=ENERGY_MOOD_CHOICES,
    #     max_length=9,
    # )
    mood = models.CharField(
        verbose_name='Настроение',
        choices=ENERGY_MOOD_CHOICES,
        max_length=9,
    )
    note = models.CharField(
        verbose_name='Заметка',
        max_length=255,
        blank=True,
        null=True
    )
    date = models.DateTimeField(
        # verbose_name=_('add date'),
        verbose_name=_('Дата/время добавления показателей'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Состояние (сотрудника)'
        verbose_name_plural = 'Состояния'

    def __str__(self):
        return self.mood

    # Для админки не вижу смысла, а в сериализаторах не работает
    # def clean(self):
    #     current_time = timezone.localtime()
    #     last_add_date = Condition.objects.filter(
    #         employee=self.employee
    #     ).order_by('-date').first()
    #     if last_add_date and (
    #             current_time - last_add_date.date
    #     ) < timezone.timedelta(hours=24):
    #         raise ValidationError(
    #             'Можно добавлять значения не чаще, чем раз в сутки!')


class Survey(models.Model):
    """Опрос."""

    author = models.ForeignKey(
        User,
        verbose_name='автор опроса',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    department = models.ForeignKey(
        Department,
        verbose_name='отдел',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
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


class Question(models.Model):
    """Вопрос к опросу."""

    survey = models.ForeignKey(
        Survey,
        verbose_name='опрос',
        on_delete=models.CASCADE,
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
        LOW = 'Низкий уровень'
        MEDIUM = 'Средний уровень'
        HIGH = 'Высокий уровень'
        CRITICAL = 'Критический уровень'

    employee = models.ForeignKey(
        User,
        verbose_name='сотрудник',
        on_delete=models.CASCADE,
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
        validators=[MaxValueValidator(10)],
    )
    negative_value = models.PositiveSmallIntegerField(
        verbose_name='кол-во отрицательных ответов',
        validators=[MaxValueValidator(10)],
    )
    completion_date = models.DateField(
        verbose_name='дата и время прохождения опроса',
        default=timezone.now,
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'результат опроса сотрудника'
        verbose_name_plural = 'результаты опросов сотрудников'

        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'survey', 'completion_date'],
                name='unique_day_completed_survey',
            ),
            models.CheckConstraint(
                check=models.Q(
                    positive_value=(10 - models.F('negative_value'))
                ), name='check_sum_results',
            ),
        ]

    def __str__(self):
        return (f'"{self.survey.title}" пройден '
                f'сотрудником {self.employee.get_full_name}')

    def save(self, *args, **kwargs):
        """При создании объекта интерпретирует значение результата в текст."""
        if self.positive_value in (7, 8, 9):
            self.result = self.ResultInterpretation.HIGH
        elif self.positive_value in (2, 3, 4, 5, 6):
            self.result = self.ResultInterpretation.MEDIUM
        elif self.positive_value in (0, 1):
            self.result = self.ResultInterpretation.LOW
        elif self.positive_value == 10:
            self.result = self.ResultInterpretation.CRITICAL
        return super(CompletedSurvey, self).save(*args, **kwargs)
