from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from notifications.models import Notification
from notifications.signals.handlers import notification

from ..models import Event

User = get_user_model()


@receiver(m2m_changed, sender=Event.departments.through)
def create_notification_for_event_by_departments(
    action, pk_set, instance, **kwargs
):
    """Вызывается при cвязывании объекта модели `Event` с `Department`.

    В результате в БД создаются объекты модели `Notification`
    для всех пользователей из поля `employees` модели `Event`
    и пользователей связанных с департаментами - полем
    `departments`.
    """
    if action == 'post_add':
        results = Notification.objects.bulk_create([
            Notification(
                incident_type=Notification.IncidentType.EVENT,
                incident_id=instance.id,
                user=obj
            ) for obj in User.objects.filter(
                Q(department__in=pk_set) & Q(is_active=True)
            )
        ])
        for obj in results:
            notification.send(sender=Notification, instance=obj)


@receiver(m2m_changed, sender=Event.employees.through)
def create_notification_for_event_by_employees(
    action, pk_set, instance, **kwargs
):
    """Вызывается при cвязывании объекта модели `Event` с `User`.

    В результате в БД создаются объекты модели `Notification`
    для всех пользователей из поля `employees` модели `Event`
    и пользователей связанных с департаментами - полем
    `departments`.
    """
    if action == 'post_add':
        results = Notification.objects.bulk_create([
            Notification(
                incident_type=Notification.IncidentType.EVENT,
                incident_id=instance.id,
                user=obj
            ) for obj in User.objects.filter(
                Q(id__in=pk_set) & Q(is_active=True)
            )
        ])
        for obj in results:
            notification.send(sender=Notification, instance=obj)
