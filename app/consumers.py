from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
import json
from .models import *


class OrderProgress(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["uid"]
        self.room_group_name = "order_%s" % self.room_name
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        order = await sync_to_async(OrderPlaced.send_status)(self.room_name)
        await self.accept()
        await self.send(text_data=json.dumps({"payload": order}))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "order_status",
                "payload": text_data,
            },
        )

    async def order_status(self, event):
        order = json.loads(event["value"])
        await self.send(text_data=json.dumps({"payload": order}))
