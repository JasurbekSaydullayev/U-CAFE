from django.urls import re_path
from orders.consumers import OrderStatusConsumer, NewOrderConsumer

websocket_urlpatterns = [
    re_path(r'ws/orders/status/$', OrderStatusConsumer.as_asgi()),
    re_path(r'ws/new-orders/$', NewOrderConsumer.as_asgi()),
]
