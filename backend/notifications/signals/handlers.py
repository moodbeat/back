from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Count
from django.dispatch import Signal, receiver

from ..models import Notification

notification = Signal()


@receiver(notification, sender=Notification)
def get_data_for_websocket(sender, user, **kwargs):
    """Вызывается при создании нового объекта модели `Notification`.

    Отправляются данные пользователю в вебсокет.
    Формат отправляемых данных:
        `counts` - количество `событий` по типам
        `events` - идентификаторы `событий` и их типы
        `
        {
            'counts': [{'incident_type': 'Опрос', 'incident_count': 10},],
            'events': [{'incident_type': 'Опрос', 'incident_id': 1},]
        }
        `
    """
    channel_layer = get_channel_layer()
    group_name = 'user_%s' % user.id
    events = user.notifications.filter(is_viewed=False).values(
        'incident_type', 'incident_id'
    )
    counts = user.notifications.filter(is_viewed=False).values(
        'incident_type'
    ).annotate(
        incident_count=Count('incident_type')
    )
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'notification',
            'message': {
                'counts': list(counts),
                'events': list(events)
            }
        }
    )
