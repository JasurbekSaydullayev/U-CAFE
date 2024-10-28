from rest_framework import serializers

from foods.models import Food


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ('id', 'name', 'price', 'count', 'category', 'day',
                  'is_active', 'image')


class FoodDetailSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    updated_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Food
        fields = ('id', 'name', 'price', 'count',
                  'created_at', 'updated_at', 'category', 'day', 'is_active', 'image')
