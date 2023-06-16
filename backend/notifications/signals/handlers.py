from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver

from ..models import Notification

notification = Signal()


@receiver([post_save, notification], sender=Notification)
def get_data_for_websocket(sender, instance, **kwargs):
    """Вызывается при создании нового объекта модели `Notification`.

    Отправляются данные пользователю в вебсокет.
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
    notifications = instance.user.notifications.filter(is_viewed=False).values(
        'id', 'incident_type', 'incident_id',
    )
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'notification',
            'message': {
                'notifications': list(notifications)
            }
        }
    )
