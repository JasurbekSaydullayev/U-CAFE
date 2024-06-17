from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from orders.models import Order
import asyncio
import json


class OrderStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.order_id = self.scope['url_route']['kwargs']['order_id']
            self.group_name = f"order_{self.order_id}"
            user = self.scope["user"]

            order = await sync_to_async(Order.objects.get)(id=self.order_id)

            if user.is_authenticated and (user.is_superuser or order.user == user):
                await self.channel_layer.group_add(
                    self.group_name,
                    self.channel_name
                )

                data = {
                    "order_id": order.id,
                    "status": order.status,
                    "status_pay": order.status_pay,
                    "order_type": order.order_type,
                    "pay_type": order.pay_type
                }

                await self.accept()
                await self.send(text_data=json.dumps(data))
            else:
                await self.close()
        except Exception as e:
            await self.send(text_data=json.dumps({"error": str(e)}))
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

            # Отправить новые заказы при подключении
            new_orders = await self.get_new_orders()
            await self.send_new_orders(new_orders)
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

    @sync_to_async
    def get_new_orders(self):
        return list(Order.objects.filter(status='new').select_related('user').all())

    @sync_to_async
    def calculate_order_price(self, order):
        return order.calculate_order_price()

    async def send_new_orders(self, orders):
        for order in orders:
            total_price = await self.calculate_order_price(order)
            data = {
                'order_id': order.id,
                'status': order.status,
                'user': order.user.full_name if order.user else 'Anonymous',
                'total_price': total_price,
                'created_at': order.created_at.isoformat(),
            }
            await self.send(text_data=json.dumps(data))
