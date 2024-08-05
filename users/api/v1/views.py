from django.contrib.auth.hashers import make_password

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.api.v1.serializers import UserDashboardSerializer, UserDetailSerializer
from users.models import User
from users.validators import check_phone_number


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ['create', 'list', 'delete', 'update']:
            return UserDashboardSerializer
        elif self.action in ['retrieve', 'partial_update']:
            return UserDetailSerializer

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


# class ChangePassword(APIView):
#     def post(self, request, *args, **kwargs):
#
