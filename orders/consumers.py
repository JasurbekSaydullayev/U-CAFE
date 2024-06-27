from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from orders.models import Order
import json


class OrderStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.group_name = f"user_{self.user.id}"
        if self.user.is_authenticated:
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def order_status(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))


class NewOrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "new_orders"
        user = self.scope["user"]

        if user.is_authenticated and user.is_superuser:
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )

            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def new_order(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))

