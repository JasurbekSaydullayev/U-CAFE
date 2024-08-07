# from rest_framework import serializers
#
# from ..v1.serializers import OrderPaymentsSerializer
# from ...DRY import serializer_dry
# from ...models import Order, OrderItem
# from foods.models import Food
#
# from decouple import config
#
#
# class OrderItemSerializerV2(serializers.ModelSerializer):
#     food_id = serializers.PrimaryKeyRelatedField(queryset=Food.objects.all(), source='food')
#     quantity = serializers.IntegerField(default=1)
#
#     class Meta:
#         model = OrderItem
#         fields = ['food_id', 'quantity']
#
#
# class OrderSerializerV2(serializers.ModelSerializer):
#     items = OrderItemSerializerV2(many=True)
#     full_price = serializers.CharField(read_only=True)
#     webhook_url = serializers.CharField(read_only=True)
#     delivery_status = serializers.CharField(read_only=True)
#     user = serializers.CharField(read_only=True)
#     payments = OrderPaymentsSerializer(many=True)
#
#     class Meta:
#         model = Order
#         fields = ['id', 'user', 'payments', 'status', 'order_type', 'items', 'status_pay', 'full_price', 'webhook_url',
#                   'delivery_status']
#
#     def create(self, validated_data):
#         return serializer_dry(self, validated_data)
#
#     def generate_webhook_url(self, order):
#         return f'ws://{config("SITE_URL")}/ws/orders/{order.id}/?token='
#
#
# class OrderDetailSerializerV2(serializers.ModelSerializer):
#     items = OrderItemSerializerV2(many=True)
#
#     class Meta:
#         model = Order
#         fields = "__all__"
