from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone
from users.models import Department

User = get_user_model()


class Category(models.Model):

    name = models.CharField(
        verbose_name='Наименование',
        unique=True,
        max_length=48,
        validators=[MinLengthValidator(2)]
    )
    slug = models.SlugField(
        unique=True,
        max_length=32,
        verbose_name='Слаг'
    )
    description = models.TextField(
        verbose_name='Описание',
        max_length=254,
        null=True,
        blank=True,
        validators=[MinLengthValidator(8)]
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Entry(models.Model):

    title = models.CharField(
        verbose_name='Заголовок',
        max_length=128,
        validators=[MinLengthValidator(2)]
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.SET_NULL,
        related_name='entries',
        null=True
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        related_name='entries',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    preview_image = models.ImageField(
        verbose_name='Превью-изображение записи',
        upload_to='entries/'
    )
    text = models.TextField(
        verbose_name='Текст',
        validators=[MinLengthValidator(8)]
    )
    created = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        ordering = ['-created']

    def __str__(self):
        return self.title


class Event(models.Model):

    name = models.CharField(
        verbose_name='Наименование',
        max_length=64,
        validators=[MinLengthValidator(2)]
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='authored_events'
    )
    departments = models.ManyToManyField(
        Department,
        verbose_name='Отдел(ы)',
        related_name='events',
        blank=True
    )
    employees = models.ManyToManyField(
        User,
        verbose_name='Сотрудники',
        related_name='participated_events',
        blank=True
    )
    text = models.TextField(
        verbose_name='Текст',
        validators=[MinLengthValidator(8)]
    )
    created = models.DateTimeField(
        auto_now_add=True
    )
    start_time = models.DateTimeField(
        verbose_name='Дата и время начала'
    )
    end_time = models.DateTimeField(
        verbose_name='Дата и время окончания'
    )

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'
        ordering = ['-created']

    def __str__(self):
        return self.name

    def clean(self):

        if self.start_time >= self.end_time:
            raise ValidationError(
                'Дата и время начала должны быть раньше даты и времени '
                'окончания.'
            )

        current_time = timezone.localtime()
        # wtf???
        if self.start_time >= current_time:
            raise ValidationError(
                'Дата и время начала должна быть не раньше текущего времени.'
            )

        time_difference = self.end_time - self.start_time
        if (
            time_difference.total_seconds() < 1800
            or time_difference.total_seconds() > 43200
        ):
            raise ValidationError(
                'Разница между датой и временем начала и окончания должна '
                'быть от 30 минут до 12 часов.'
            )
