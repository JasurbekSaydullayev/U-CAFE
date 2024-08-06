from django.contrib.auth.hashers import make_password, check_password
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from pagination import StandardResultsSetPagination
from users.api.v1.serializers import UserDashboardSerializer, UserDetailSerializer, ChangePasswordSerializer
from users.models import User
from users.validators import check_phone_number

from ...models import user_type


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action in ['create', 'list', 'delete', 'update']:
            return UserDashboardSerializer
        elif self.action in ['retrieve', 'partial_update']:
            return UserDetailSerializer

    def list(self, request, *args, **kwargs):
        users = User.objects.all()
        serializer = self.get_serializer(users, many=True)
        page = self.paginate_queryset(serializer.data)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
                'type': openapi.Schema(type=openapi.TYPE_STRING, enum=[e[0] for e in user_type]),
                'full_name': openapi.Schema(type=openapi.TYPE_STRING),
                'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
                'salary': openapi.Schema(type=openapi.TYPE_INTEGER),
            },
            required=['username', 'password', 'type', 'full_name', 'phone_number'],
        )
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
            if not check_phone_number(serializer.validated_data['phone_number']):
                return Response({"message": "Telefon raqam noto'g'ri kiritildi"}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class GetUserInfo(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        return Response(
            {
                "id": user.id,
                "full_name": user.full_name,
                "phone_number": user.phone_number,
                "type": user.type,
                "username": user.username,
            })


class ChangePassword(APIView):
    serializer_class = ChangePasswordSerializer
    # authentication_classes = []
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'old_password': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
                'password2': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['old_password', 'password', 'password2'],
        )
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            old_password = serializer.validated_data['old_password']
            right_old_password = request.user.password
            if check_password(old_password, right_old_password):
                password = serializer.validated_data['password']
                password2 = serializer.validated_data['password2']
                if password != password2:
                    return Response({"message": "Password mismatch"}, status=status.HTTP_400_BAD_REQUEST)
                request.user.set_password(password)
                request.user.save()
                return Response({"status": True, "message": "Пароль успешно изменен"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Old password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
