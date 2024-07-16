from rest_framework import serializers

from foods.models import Food, Photo


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = '__all__'

    def validate(self, data):
        file = data.get('file')
        if file.size > 1024 * 1024:  # 1 MB
            raise serializers.ValidationError("File size exceeds the limit of 1 MB")
        return data


class FoodSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Food
        fields = ('id', 'name', 'price', 'count', 'category',
                  'is_active', 'photos')


class FoodDetailSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    updated_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Food
        fields = ('id', 'name', 'price', 'count',
                  'created_at', 'updated_at', 'category', 'day', 'is_active', 'photos')
