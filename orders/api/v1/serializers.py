from rest_framework import serializers

from foods.api.v1.serializers import FoodSerializer
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
        fields = ['id', 'pay_type', 'status', 'order_type', 'items', 'status_pay', 'position',
                  'full_price', 'webhook_url', 'created_at', 'delivery_status']

    def create(self, validated_data):
        return serializer_dry(self, validated_data)

    def update(self, instance, validated_data):
        if instance.status == 'completed':
            raise serializers.ValidationError(
                {"status": False, 'msg': "Tugatilgan yoki jarayondagi buyurtmani o'zgartirish mumkin emas"})

        items_data = validated_data.pop('items', None)

        instance.pay_type = validated_data.get('pay_type', instance.pay_type)
        instance.status = validated_data.get('status', instance.status)
        instance.order_type = validated_data.get('order_type', instance.order_type)
        instance.status_pay = validated_data.get('status_pay', instance.status_pay)
        instance.save()

        print(instance.items)

        return instance


class OrderItemSerializerForDetailView(serializers.ModelSerializer):
    food = FoodSerializer(read_only=True)
    quantity = serializers.IntegerField(default=1)

    class Meta:
        model = OrderItem
        fields = ['food', 'quantity']


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializerForDetailView(many=True)

    class Meta:
        model = Order
        fields = "__all__"
