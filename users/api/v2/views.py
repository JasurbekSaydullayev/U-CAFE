from rest_framework import viewsets, status

from rest_framework.permissions import AllowAny

from users.api.v2.serializers import UserSerializerV2
from users.models import User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializerV2


