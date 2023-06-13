from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Notification(models.Model):
    """Модель для уведомлений пользователей."""

    class IncidentType(models.TextChoices):
        SURVEY = 'Опрос'
        EVENT = 'Событие'
        MESSAGE = 'Сообщение'

    incident_type = models.TextField(
        verbose_name='тип уведомления',
        choices=IncidentType.choices,
        blank=True
    )
    user = models.ForeignKey(
        User,
        verbose_name='сотрудник',
        related_name='notifications',
        on_delete=models.CASCADE
    )
    is_viewed = models.BooleanField(
        verbose_name='просмотрено/не просмотрено',
        default=False
    )
    creation_date = models.DateTimeField(
        verbose_name='дата и время создания уведомления',
        default=timezone.now,
    )

    class Meta:
        ordering = ('-creation_date',)
        verbose_name = 'уведомление'
        verbose_name_plural = 'уведомления'

    def __str__(self):
        return f'Уведомление №{self.id} для пользователя {self.user}'
