from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from notifications.models import Notification

from ..models import NeedHelp


@receiver(post_save, sender=NeedHelp)
def create_notification_for_help_type(sender, instance, created, **kwargs):
    """Вызывается после сохранения объекта `NeedHelp`.

    В результате, в БД создаются объекты модели `Notification`
    для пользователя из поля `recipient` модели `NeedHelp`.
    """
    if created and instance.recipient.is_active:
        Notification.objects.create(
            incident_type=Notification.IncidentType.HELP,
            incident_id=instance.id,
            user=instance.recipient
        )


@receiver(post_delete, sender=NeedHelp)
def delete_notifications_after_obj_help_type_delete(
    sender, instance, *args, **kwargs
):
    """Вызывается после удаления объекта `NeedHelp`.

    Удаляются все уведомления, связанные с удаляемым экземпляром `NeedHelp`.
    """
    Notification.objects.filter(
        incident_id=instance.id,
        incident_type=Notification.IncidentType.HELP
    ).delete()
