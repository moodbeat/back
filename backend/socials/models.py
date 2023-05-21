from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.db import models

User = get_user_model()


class HelpType(models.Model):

    HR = 'hr'
    CHIEF = 'chief'

    ROLES = (
        (HR, 'HR'),
        (CHIEF, 'Руководитель')
    )

    title = models.CharField(
        verbose_name='Тип помощи',
        max_length=32,
        unique=True,
        validators=[MinLengthValidator(2)]
    )
    description = models.TextField(
        verbose_name='Описание',
        max_length=128,
        null=True,
        blank=True,
        validators=[MinLengthValidator(8)]
    )
    role = models.CharField(
        verbose_name='Роль',
        choices=ROLES,
        max_length=10,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Тип помощи'
        verbose_name_plural = 'Типы помощи'

    def __str__(self):
        return self.title


class NeedHelp(models.Model):

    sender = models.ForeignKey(
        User,
        verbose_name='Отправитель',
        related_name='sent_help_requests',
        on_delete=models.SET_NULL,
        null=True
    )
    recipient = models.ForeignKey(
        User,
        verbose_name='Получатель',
        related_name='received_help_requests',
        on_delete=models.SET_NULL,
        null=True
    )
    type = models.ForeignKey(
        HelpType,
        verbose_name='Тип помощи',
        related_name='employees',
        on_delete=models.SET_NULL,
        null=True
    )
    comment = models.TextField(
        verbose_name='Комментарий',
        max_length=496,
        validators=[MinLengthValidator(4)]
    )
    viewed = models.BooleanField(
        verbose_name='Просмотрено',
        default=False
    )
    created = models.DateTimeField(
        verbose_name='Дата и время отправки',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Запрос помощи'
        verbose_name_plural = 'Запросы помощи'
