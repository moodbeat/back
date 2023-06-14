import json

from channels.generic.websocket import AsyncWebsocketConsumer


class UserNotifyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_authenticated:
            self.ws_id = self.scope['user'].id
            self.group_name = 'user_%s' % self.ws_id
            await self.channel_layer.group_add(
                self.group_name, self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        if self.scope['user'].is_authenticated:
            await self.channel_layer.group_discard(
                self.group_name, self.channel_name
            )
        await self.close()

    async def notification(self, event):
        message = event['message']
        await self.send(json.dumps({'message': message}))
