# orders/routing.py

from django.urls import re_path
from orders.consumers import OrderStatusConsumer

websocket_urlpatterns = [
    re_path(r'ws/orders/(?P<order_id>\d+)/$', OrderStatusConsumer.as_asgi()),
]
