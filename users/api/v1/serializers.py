from rest_framework import serializers

from users.models import User


class UserDashboardSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, max_length=128, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'phone_number', 'salary', 'full_name', 'type', 'is_active', 'password')


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'full_name', 'type', 'is_active', 'phone_number', 'last_login',
                  'date_joined',)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128, write_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    password2 = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        fields = ('old_password', 'password', 'password2')
