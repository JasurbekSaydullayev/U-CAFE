from django.core.cache import cache
from django.contrib.auth.hashers import make_password

from rest_framework import serializers

from users.models import User
from users.validators import check_phone_number


class UserSerializerV2(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone_number']

    def create(self, validated_data):
        if not check_phone_number(validated_data['phone_number']):
            raise serializers.ValidationError({'message': "Telefon raqam noto'g'ri kiritildi"})
        cache.set(key=f"{validated_data['phone_number']}", value=validated_data['phone_number'][-4:], timeout=60 * 5)
        return validated_data


class UserConfirmWithCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    code = serializers.CharField()

    class Meta:
        fields = ['phone_number', 'code']
