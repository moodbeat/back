from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
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
    author = models.ForeignKey(
        User,
        verbose_name='Сотрудник, автор опроса',
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
        # verbose_name=_('creation date'),
        verbose_name=_('Дата/время создания опроса'),
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
        return self.description[:30]


class Variant(models.Model):
    # убрала отсюда результат, потому что не оч понятно, к чему он тут относится
    ANSWERS = (
        ('Yes', _('Да')),
        ('No', _('Нет')),
        ('Never', _('Никогда')),
        ('Seldom', _('Очень редко')),
        ('Sometimes', _('Иногда')),
        ('Often', _('Часто')),
        ('Very often', _('Очень часто')),
        ('Every day', _('Каждый день')),
    )

    question = models.ForeignKey(
        Question,
        verbose_name='Вопрос',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    text = models.CharField(
        verbose_name='Текст варианта ответа',
        choices=ANSWERS,
        max_length=12,
    )

    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответов'

    def __str__(self):
        return f'Ответ {self.text} на вопрос "{self.question.text[:30]}"'


class CompletedSurvey(models.Model):
    employee = models.ForeignKey(
        User,
        verbose_name='Сотрудник',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    survey = models.ForeignKey(
        Survey,
        verbose_name='Опрос',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    result = models.ForeignKey(
        Result,
        verbose_name='Результат опроса',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    completion_date = models.DateTimeField(
        # verbose_name=_('completion date'),
        verbose_name=_('Дата/время завершения опроса'),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Завершенный опрос'
        verbose_name_plural = 'Завершенные опросы'

    def __str__(self):
        return (f'"{self.survey.title}" пройден '
               f'сотрудником {self.employee.last_name}')
