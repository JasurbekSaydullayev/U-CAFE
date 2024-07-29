from rest_framework import serializers

from ...models import Food


class FoodSerializerV2(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ('id', 'name', 'price', 'count',
                  'is_active', 'image')


class FoodDetailSerializerV2(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    updated_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Food
        fields = ('id', 'name', 'price', 'count',
                  'created_at', 'updated_at', 'category', 'day', 'is_active', 'image')
