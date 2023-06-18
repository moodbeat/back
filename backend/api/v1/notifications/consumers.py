import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models import Q

from notifications.models import Notification


class UserNotifyConsumer(AsyncWebsocketConsumer):
    @sync_to_async
    def get_list_notifications(self):
        return list(Notification.objects.filter(
            Q(user_id=self.ws_id) & Q(is_viewed=False)
        ).values(
            'id', 'incident_type', 'incident_id',
        ))

    async def connect(self):
        if self.scope['query_string']:
            self.ws_id = int(self.scope['query_string'])
            self.group_name = 'user_%s' % self.ws_id
            await self.channel_layer.group_add(
                self.group_name, self.channel_name
            )
            await self.accept()
            notifications = await self.get_list_notifications()
            await self.send(json.dumps(
                {'message': {
                    'notifications': notifications
                }},
                ensure_ascii=False,
            ))

    async def disconnect(self, close_code):
        if self.scope['query_string']:
            await self.channel_layer.group_discard(
                self.group_name, self.channel_name
            )
        await self.close()

    async def notification(self, event):
        message = event['message']
        await self.send(json.dumps({'message': message}, ensure_ascii=False))
