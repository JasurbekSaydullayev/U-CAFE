from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import viewsets

from complaints.api.v1.serializers import ComplaintSerializerV1
from complaints.models import Complaint
from permissions import IsAdminOrOwner, IsAdmin


class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializerV1
    http_method_names = ['get']

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), AllowAny()]
        elif self.action == 'list':
            return [IsAuthenticated(), IsAdmin()]
        elif self.action == 'retrieve':
            return [IsAuthenticated(), IsAdminOrOwner()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, phone_number=self.request.user.phone_number)
