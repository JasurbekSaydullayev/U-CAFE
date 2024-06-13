from django.contrib.auth.hashers import make_password

from rest_framework import viewsets, status
from rest_framework.response import Response

from users.api.v1.serializers import UserSerializer, UserDetailSerializer
from users.models import User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ['create', 'list', 'delete', 'update']:
            return UserSerializer
        elif self.action in ['retrieve', 'partial_update']:
            return UserDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
