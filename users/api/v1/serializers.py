from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User


class UserDashboardSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, max_length=128, write_only=True)
    date_joined = serializers.DateTimeField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'phone_number', 'salary', 'full_name', 'type', 'is_active', 'password', 'date_joined')


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


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['full_name'] = user.full_name
        token['username'] = user.username
        token['user_type'] = user.type
        token['phone_number'] = user.phone_number
        token['salary'] = user.salary
        token['date_joined'] = user.date_joined.isoformat()
        return token
