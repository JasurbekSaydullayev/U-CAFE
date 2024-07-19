from rest_framework import serializers

from orders.DRY import serializer_dry
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
        fields = ['id', 'pay_type', 'status', 'order_type', 'items', 'status_pay',
                  'full_price', 'webhook_url', 'created_at', 'delivery_status']

    def create(self, validated_data):
        return serializer_dry(self, validated_data)


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = "__all__"
