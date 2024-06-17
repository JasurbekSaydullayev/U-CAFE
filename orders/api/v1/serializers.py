from rest_framework import serializers
from orders.models import Order, OrderItem
from foods.models import Food
from decouple import config


class OrderItemSerializer(serializers.ModelSerializer):
    food_id = serializers.PrimaryKeyRelatedField(queryset=Food.objects.all(), source='food')
    quantity = serializers.IntegerField(default=1)

    class Meta:
        model = OrderItem
        fields = ['food_id', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    full_price = serializers.CharField(read_only=True)
    webhook_url = serializers.CharField(read_only=True)
    delivery_status = serializers.CharField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'pay_type', 'status', 'order_type', 'items', 'status_pay', 'full_price', 'webhook_url',
                  'delivery_status']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            food = item_data['food']
            quantity = item_data['quantity']
            if food.count < quantity:
                raise serializers.ValidationError({"message": f"{food.name} dan siz so'ragan miqdorda qolmagan"})
            food.count -= quantity
            food.save()
            price = food.price * quantity
            OrderItem.objects.create(order=order, food=food, quantity=quantity, price=price)
        if order.order_type == "delivery":
            order.delivery_status = "waiting"
        else:
            order.delivery_status = None
        order.full_price = order.calculate_order_price()
        order.position = len(items_data)
        order.webhook_url = self.generate_webhook_url(order)
        order.save()
        return order

    def generate_webhook_url(self, order):
        return f'ws://{config("SITE_URL")}/ws/orders/{order.id}/'


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = "__all__"
