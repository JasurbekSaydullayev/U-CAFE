from django.db.models.signals import post_save
from django.utils import timezone
from datetime import timedelta

from rest_framework import serializers
from .models import Order, OrderItem
from .signals import order_status_update


def dry(request):
    start_date = request.query_params.get('start_date', (timezone.now() - timedelta(days=30)).date())
    end_date = request.query_params.get('end_date', timezone.now().date())
    if isinstance(start_date, str):
        start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()

    start_date = timezone.make_aware(timezone.datetime.combine(start_date, timezone.datetime.min.time()))
    end_date = timezone.make_aware(timezone.datetime.combine(end_date, timezone.datetime.max.time()))
    return start_date, end_date


def serializer_dry(self, validated_data):
    items_data = validated_data.pop('items')
    for item in items_data:
        if item['food'].count < item['quantity']:
            raise serializers.ValidationError({"message": f"{item['food'].name} dan siz so'ragan miqdorda qolmagan"})
    post_save.disconnect(receiver=order_status_update, sender=Order)
    order = Order.objects.create(**validated_data)
    total_price = 0
    for item_data in items_data:
        food = item_data['food']
        quantity = item_data['quantity']
        food.count -= quantity
        food.save()
        price = food.price * quantity
        total_price += price
        OrderItem.objects.create(order=order, food=food, quantity=quantity, price=price)
    if order.order_type == "delivery":
        order.delivery_status = "waiting"
    else:
        order.delivery_status = None
    order.status_pay = 'unpaid'
    order.status = 'new'
    order.full_price = total_price
    order.position = len(items_data)
    post_save.connect(receiver=order_status_update, sender=Order)
    order.save()
    return order
