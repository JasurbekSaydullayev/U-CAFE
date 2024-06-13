from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from orders.models import Order
import asyncio


class OrderStatusConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

        path = self.scope['path']
        self.order_id = path.strip('/').split('/')[-1]

        await self.monitor_order_status()

    async def monitor_order_status(self):
        while True:
            order = await sync_to_async(Order.objects.get)(id=self.order_id)
            status = order.status

            await self.send(text_data=f"Order {self.order_id} status: {status}")

            if status == 'completed':
                await self.close()
                break

            await asyncio.sleep(10)

    async def disconnect(self, close_code):
        pass
