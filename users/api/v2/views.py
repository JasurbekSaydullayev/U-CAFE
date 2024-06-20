from django.core.cache import cache

from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from permissions import IsAdminOrOwner
from users.api.v2.serializers import UserSerializerV2, UserConfirmWithCodeSerializer
from users.models import User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializerV2
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        elif self.action in ['list', 'retrieve', 'update', 'destroy']:
            return [IsAuthenticated, IsAdminOrOwner]

    def list(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response({"message": "Siz allaqachon ro'yhatdan o'tgansiz"},
                            status=status.HTTP_200_OK)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Tasdiqlash uchun kod jo'natildi"}, status=status.HTTP_200_OK)


class UserConfirmWithCodeViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserConfirmWithCodeSerializer
    permission_classes = [AllowAny]
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            phone_number = serializer.validated_data['phone_number']
            code = serializer.validated_data['code']
            user_code = cache.get(key=f"{phone_number}")
            if not user_code:
                return Response({"Bunday telefon raqam bilan tasdiqlanishi kerak bo'lgan mijoz topilmadi"},
                                status=status.HTTP_200_OK)
            if code != user_code:
                return Response({"message": "Tasdiqlash kodi xato kiritildi"},
                                status=status.HTTP_200_OK)
            else:
                user = User.objects.create(type='Customer', phone_number=phone_number, username=f"{phone_number}")
                user.set_password(serializer.validated_data['phone_number'][-4:])
                user.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
