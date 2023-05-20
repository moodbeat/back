from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from metrics.validators import validate_last_filled_date
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

    user = models.ForeignKey(
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
        verbose_name=_('add date'),
        default=timezone.now,
        validators=[validate_last_filled_date]
    )

    class Meta:
        verbose_name = 'Состояние (сотрудника)'
        verbose_name_plural = 'Состояния'

    def __str__(self):
        return (
            f'Настроение {self.user.first_name} {self.user.last_name} - '
            f'{self.mood} '
        )


class Survey(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Сотрудник',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    department = models.ForeignKey(
        Department,
        verbose_name='Отдел',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    title = models.CharField(
        verbose_name='Название опроса',
        max_length=255,
    )
    description = models.CharField(
        verbose_name='Описание опроса',
        blank=True,
        null=True,
        max_length=255,
    )
    creation_date = models.DateTimeField(
        verbose_name=_('creation date'),
        default=timezone.now,
    )
    is_active = models.BooleanField(
        verbose_name='Статус активности',
        default=True,
    )

    class Meta:
        verbose_name = 'Опрос'
        verbose_name_plural = 'Опросы'

    def __str__(self):
        return self.title


class Question(models.Model):
    survey = models.ForeignKey(
        Survey,
        verbose_name='Опрос',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    text = models.CharField(
        verbose_name='Текст вопроса',
        max_length=255,
    )
    priority = models.PositiveSmallIntegerField(
        verbose_name='Приоритет',
        blank=True,
        null=True,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return self.text


class Result(models.Model):
    survey = models.ForeignKey(
        Survey,
        verbose_name='Опрос',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    description = models.TextField(verbose_name='Описание')
    level = models.PositiveSmallIntegerField(
        verbose_name='Уровень',
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    class Meta:
        verbose_name = 'Результат'
        verbose_name_plural = 'Результаты'

    def __str__(self):
        return self.description


class Variant(models.Model):
    question = models.ForeignKey(
        Question,
        verbose_name='Вопрос',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    text = models.CharField(
        verbose_name='Текст варианта ответа',
        max_length=255,
    )

    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответов'