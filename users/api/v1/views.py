from django.contrib.auth.hashers import make_password, check_password
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from pagination import StandardResultsSetPagination
from permissions import IsManager, IsAdmin, IsAdminOrManager
from users.api.v1.serializers import UserDashboardSerializer, UserDetailSerializer, ChangePasswordSerializer, \
    CustomTokenObtainPairSerializer, ChangePasswordForSuperAdmin, UploadImageUserSerializer, EditProfileSerializer, \
    EditProfileForSuperAdminOrManagerSerializer
from users.models import User
from users.validators import check_phone_number

from ...models import user_type


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsManager]

    def get_serializer_class(self):
        if self.action in ['create', 'list', 'delete', 'update']:
            return UserDashboardSerializer
        elif self.action in ['retrieve', 'partial_update']:
            return UserDetailSerializer

    def list(self, request, *args, **kwargs):
        users = User.objects.filter(is_superuser=False).all().order_by('-date_joined')
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
                'user_type': openapi.Schema(type=openapi.TYPE_STRING, enum=[e[0] for e in user_type]),
                'full_name': openapi.Schema(type=openapi.TYPE_STRING),
                'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
                'salary': openapi.Schema(type=openapi.TYPE_INTEGER),
            },
            required=['username', 'password', 'user_type', 'full_name', 'phone_number'],
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
                "user_type": user.user_type,
                "username": user.username,
                "image": user.image.url if user.image else None
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


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user

        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            user_info = {
                "id": user.id,
                'full_name': user.full_name,
                'username': user.username,
                'user_type': user.user_type,
                'phone_number': user.phone_number,
                'salary': user.salary,
                'date_joined': user.date_joined.isoformat(),
            }
            response.data['user'] = user_info
        return response


class ChangePasswordEmployeesForSuperAdmins(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = ChangePasswordForSuperAdmin

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['id', 'password'],
        ))
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user_id = serializer.validated_data['id']
            password = serializer.validated_data['password']
            user = User.objects.filter(id=user_id).first()
            if not user:
                return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            user.set_password(password)
            user.save()
            return Response({'status': "True", "message": "Successfully"}, status=status.HTTP_201_CREATED)


class UploadPhotoUser(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = UploadImageUserSerializer

    @swagger_auto_schema(
        request_body=UploadImageUserSerializer,
        manual_parameters=[
            openapi.Parameter(
                'image', openapi.IN_FORM, type=openapi.TYPE_FILE, description='Upload image'
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(user, data=request.data, partial=True)
        if serializer.is_valid():
            if not request.FILES.get('image'):
                return Response({"image": ["No file was submitted."]}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EditUserInfo(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EditProfileSerializer

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
                'full_name': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=[],
        )
    )
    def patch(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EditUserInfoForSuperAdminOrManager(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = EditProfileForSuperAdminOrManagerSerializer

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'salary': openapi.Schema(type=openapi.TYPE_INTEGER),
                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
            },
            required=[],
        ),
        responses={
            200: openapi.Response(
                description="User updated successfully",
                schema=EditProfileForSuperAdminOrManagerSerializer()
            ),
            404: openapi.Response(description="User not found"),
            400: openapi.Response(description="Bad request")
        }
    )
    def patch(self, request, *args, **kwargs):
        user = User.objects.filter(id=kwargs['pk']).first()
        if not user:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeletePhotoUser(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.image:
            return Response({"message": "No image was submitted."}, status=status.HTTP_400_BAD_REQUEST)
        user.image.delete()
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
