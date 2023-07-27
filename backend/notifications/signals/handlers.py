from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from spare_kits import notification_email_service as email_service
from spare_kits.wrappers import disable_for_loaddata

from ..models import Notification


@receiver(post_save, sender=Notification)
@disable_for_loaddata
def get_data_for_websocket_post_save(sender, instance, created, **kwargs):
    """Вызывается при создании нового объекта модели `Notification`.

    Отправляются данные пользователю в вебсокет и уведомление на email.
    Формат отправляемых данных:
        `notifications` - идентификаторы уведомлений, идентификаторы `событий`
        и их типы
        `
        {
            'notifications': [
                {'id': 1, 'incident_type': 'Опрос', 'incident_id': 1},
            ]
        }
        `
    """
    channel_layer = get_channel_layer()
    group_name = 'user_%s' % instance.user.id
    notifications = list(
        instance.user.notifications.filter(is_viewed=False).values(
            'id', 'incident_type', 'incident_id',
        )
    )
    email_service.send_notification_on_email(
        instance.user,
        notifications[-1]['incident_type']
    )
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'notification',
            'message': {
                'notifications': notifications
            }
        }
    )


@receiver(pre_delete, sender=Notification)
@disable_for_loaddata
def get_data_for_websocket_pre_delete(sender, instance, **kwargs):
    """Вызывается при удалении объекта модели `Notification`.

    Отправляются обновленные данные пользователю в вебсокет.
    """
    channel_layer = get_channel_layer()
    group_name = 'user_%s' % instance.user.id
    notifications = list(
        instance.user.notifications.filter(is_viewed=False).values(
            'id', 'incident_type', 'incident_id',
        )
    )
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'notification',
            'message': {
                'notifications': notifications
            }
        }
    )
