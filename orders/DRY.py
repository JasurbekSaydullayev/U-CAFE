from django.db.models.signals import post_save
from django.utils import timezone
from datetime import timedelta

from rest_framework import serializers
from .models import Order, OrderItem, OrderPayments
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

    previous_start_date = start_date - (end_date - start_date)
    previous_end_date = start_date

    return start_date, end_date, previous_start_date, previous_end_date


def serializer_dry(self, validated_data):
    items_data = validated_data.pop('items')
    payments_data = validated_data.pop('payments')

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

    total_payment = sum(payment['price'] for payment in payments_data)
    if total_payment > total_price:
        order.delete()
        raise serializers.ValidationError({"payments": "To'lov summasi buyurtma summasidan oshib ketmoqda."})

    for payment_data in payments_data:
        if payment_data['price'] == 0:
            continue
        OrderPayments.objects.create(order=order, **payment_data)

    if order.order_type == "delivery":
        order.delivery_status = "waiting"
    else:
        order.delivery_status = None

    order.status = 'new'
    order.full_price = total_price
    order.position = len(items_data)
    order.discount = total_price - total_payment

    post_save.connect(receiver=order_status_update, sender=Order)
    order.save()
    return order
