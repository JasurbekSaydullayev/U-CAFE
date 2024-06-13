from rest_framework import serializers

from complaints.models import Complaint


class ComplaintSerializerV1(serializers.ModelSerializer):
    user = serializers.CharField(read_only=True)

    class Meta:
        model = Complaint
        fields = '__all__'
