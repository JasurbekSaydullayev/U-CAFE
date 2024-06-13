from rest_framework.response import Response
from rest_framework import viewsets

from complaints.api.v2.serializers import ComplaintSerializerV2
from complaints.models import Complaint


class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializerV2
    http_method_names = ['get', 'post']

    def list(self, request, *args, **kwargs):
        complaints = Complaint.objects.filter(user=request.user).all()
        serializer = ComplaintSerializerV2(complaints, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        try:
            phone_number = serializer.validated_data['phone_number']
        except KeyError:
            phone_number = self.request.user.phone_number
        serializer.save(user=self.request.user, phone_number=phone_number)
