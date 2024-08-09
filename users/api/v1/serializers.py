from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User

from PIL import Image


class UserDashboardSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, max_length=128, write_only=True)
    date_joined = serializers.DateTimeField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'phone_number', 'salary', 'full_name', 'user_type', 'is_active', 'password',
            'date_joined', 'image',)


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'full_name', 'user_type', 'is_active', 'phone_number', 'last_login', 'salary',
                  'date_joined', 'image')


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
        token['user_type'] = user.user_type
        token['phone_number'] = user.phone_number
        token['salary'] = user.salary
        token['date_joined'] = user.date_joined.isoformat()
        return token


class ChangePasswordForSuperAdmin(serializers.Serializer):
    id = serializers.IntegerField()
    password = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        fields = ('id', 'password')


class UploadImageUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['image']

    def validate_image(self, image):
        valid_mime_types = ['image/jpeg', 'image/png']
        max_size = 2 * 1024 * 1024  # 2 MB

        try:
            img = Image.open(image)
            img.verify()
        except Exception:
            raise ValidationError('Invalid image format. Only JPEG and PNG are allowed.')

        if img.format not in ['JPEG', 'PNG']:
            raise ValidationError('Invalid image format. Only JPEG and PNG are allowed.')

        if image.size > max_size:
            raise ValidationError('Image file too large ( > 2MB ).')

        return image


class EditProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'full_name', 'phone_number']


class EditProfileForSuperAdminOrManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'salary', 'is_active']
