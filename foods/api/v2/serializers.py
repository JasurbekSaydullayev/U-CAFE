from rest_framework import serializers

from ...models import Food, Photo


class PhotoSerializerV2(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = '__all__'


class FoodSerializerV2(serializers.ModelSerializer):
    photos = PhotoSerializerV2(many=True, read_only=True)

    class Meta:
        model = Food
        fields = ('id', 'name', 'price', 'count',
                  'is_active', 'photos')


class FoodDetailSerializerV2(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    updated_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    photos = PhotoSerializerV2(many=True, read_only=True)

    class Meta:
        model = Food
        fields = ('id', 'name', 'price', 'count',
                  'created_at', 'updated_at', 'category', 'day', 'is_active', 'photos')
