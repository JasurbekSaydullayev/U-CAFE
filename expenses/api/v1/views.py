from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from orders.DRY import dry
from permissions import IsAdmin
from .serializers import ExpenseSerializer
from expenses.models import Expenses
from pagination import StandardResultsSetPagination

manual_parameters = [
    openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, format='date',
                      description='Start date in YYYY-MM-DD format'),
    openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, format='date',
                      description='End date in YYYY-MM-DD format'),
]


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expenses.objects.all()
    serializer_class = ExpenseSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(manual_parameters=manual_parameters)
    def list(self, request, *args, **kwargs):
        start_date, end_date = dry(request)
        queryset = Expenses.objects.filter(date__range=(start_date, end_date)).order_by('-date')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
        else:
            serializer = self.get_serializer(queryset, many=True)
        return self.get_paginated_response(serializer.data)
