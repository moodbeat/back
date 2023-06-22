from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from notifications.models import Notification

from ..models import Event

User = get_user_model()


@receiver(post_save, sender=Event)
def create_notification_for_event_for_all(sender, instance, created, **kwargs):
    """Вызывается после сохранения объекта `Event`.

    Идет проверка, что объект только что создан и проверяет положительно ли
    значение параметра for_all. При этих двух условиях создаются уведомления
    для всех активных пользователей сервиса.
    """
    if created and instance.for_all:
        Notification.objects.bulk_create([
            Notification(
                incident_type=Notification.IncidentType.EVENT,
                incident_id=instance.id,
                user=obj
            ) for obj in User.objects.filter(is_active=True)
        ])


@receiver(post_delete, sender=Event)
def delete_notifications_after_obj_delete(sender, instance, *args, **kwargs):
    """Вызывается после удаления объекта `Event`.

    Удаляются все уведомления с id и типом удаленного экземпляра `Event`.
    """
    Notification.objects.filter(
        incident_id=instance.id,
        incident_type=Notification.IncidentType.EVENT
    ).delete()


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
    if action == 'post_add' and instance.for_all is False:
        Notification.objects.bulk_create([
            Notification(
                incident_type=Notification.IncidentType.EVENT,
                incident_id=instance.id,
                user=obj
            ) for obj in User.objects.filter(
                Q(department__in=pk_set) & Q(is_active=True)
            )
        ])


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
    if action == 'post_add' and instance.for_all is False:
        Notification.objects.bulk_create([
            Notification(
                incident_type=Notification.IncidentType.EVENT,
                incident_id=instance.id,
                user=obj
            ) for obj in User.objects.filter(
                Q(id__in=pk_set) & Q(is_active=True)
            )
        ])
