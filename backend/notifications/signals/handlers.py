from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Count
from django.db.models.signals import post_save
from django.dispatch import receiver

from ..models import Notification


@receiver(post_save, sender=Notification)
def get_data_for_websocket(sender, instance, **kwargs):
    """Вызывается при создании нового объекта модели `Notification`.

    Отправляются данные пользователю в вебсокет.
    """
    channel_layer = get_channel_layer()
    group_name = 'user_%s' % instance.user.id
    data = instance.user.notifications.filter(is_viewed=False).values(
        'incident_type'
    ).annotate(
        incident_count=Count('incident_type')
    )
    async_to_sync(channel_layer.group_send)(
        group_name, {"type": "notification", "data": list(data)}
    )
