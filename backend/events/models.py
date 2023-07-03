from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone

from users.models import Department, MentalState

from .validators import validate_event_data

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
    category = models.ManyToManyField(
        Category,
        verbose_name='Категория',
        related_name='entries',
        blank=True
    )
    preview_image = models.ImageField(
        verbose_name='Превью-изображение записи',
        upload_to='entries/',
        default='entries/entries_thumbnail.jpg'
    )
    description = models.TextField(
        verbose_name='Описание',
        max_length=150
    )
    url = models.URLField(
        verbose_name='Ссылка',
        max_length=500,
        null=True,
        blank=True
    )
    text = models.TextField(
        verbose_name='Текст',
        validators=[MinLengthValidator(8)],
        max_length=2000,
        null=True,
        blank=True
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

    def clean(self):

        if not self.text and not self.url:
            raise ValidationError(
                'Запись обязательно должна содержать ссылку или текст.'
            )

        if self.text and self.url:
            raise ValidationError('Введите что-то одно (текст или ссылку).')

        return super().clean()


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
    for_all = models.BooleanField(
        verbose_name='Отправка для всех',
        help_text=(
            'При положительном значении, поля с сотрудниками и отделами '
            'игнорируются и приглашения отправляются всем активным '
            'сотрудникам'
        ),
        default=False
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
        max_length=130,
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
        validate_event_data(self.start_time, self.end_time)


class MeetingResult(models.Model):

    organizer = models.ForeignKey(
        User,
        verbose_name='Организатор',
        on_delete=models.CASCADE,
        related_name='organized_meets'
    )
    employee = models.ForeignKey(
        User,
        verbose_name='Сотрудник',
        on_delete=models.CASCADE,
        related_name='meets'
    )
    date = models.DateField(
        verbose_name='Дата встречи'
    )
    mental_state = models.ForeignKey(
        MentalState,
        verbose_name='Состояние',
        related_name='meets',
        on_delete=models.CASCADE
    )
    comment = models.TextField(
        verbose_name='Комментарий',
        max_length=400
    )

    def clean(self):
        if self.date > timezone.localtime().date():
            raise ValidationError(
                'Указанная дата не может быть больше текущей.'
            )
        return super().clean()

    class Meta:
        verbose_name = 'Результат встречи'
        verbose_name_plural = 'Результаты встреч'
        ordering = ['-date']
