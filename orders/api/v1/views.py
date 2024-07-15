import requests
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Count

from orders.DRY import dry
from pagination import StandardResultsSetPagination
from permissions import IsAdmin
from .serializers import OrderItemSerializer, OrderSerializer, OrderDetailSerializer
from orders.models import Order, OrderItem
from expenses.models import Expenses


# Statistics
class IncomeAPIView(APIView):
    permission_classes = (IsAuthenticated, IsAdmin)

    def get(self, request, format=None):
        start_date, end_date = dry(request)
        total_income = Order.objects.filter(
            status='completed',
            created_at__range=(start_date, end_date)
        ).aggregate(total_income=Sum('full_price'))['total_income'] or 0
        return Response({'total_income': total_income}, status=status.HTTP_200_OK)


class ExpensesAPIView(APIView):
    permission_classes = (IsAuthenticated, IsAdmin)

    def get(self, request, format=None):
        start_date, end_date = dry(request)
        total_expenses = Expenses.objects.filter(
            date__range=(start_date, end_date)
        ).aggregate(total_expenses=Sum('price'))['total_expenses'] or 0

        return Response({'total_expenses': total_expenses}, status=status.HTTP_200_OK)


class SalesAPIView(APIView):
    permission_classes = (IsAuthenticated, IsAdmin)

    def get(self, request, format=None):
        start_date, end_date = dry(request)
        total_sales = Order.objects.filter(
            status='completed',
            created_at__range=(start_date, end_date)
        ).count()

        return Response({'total_sales': total_sales}, status=status.HTTP_200_OK)


class OrdersAPIView(APIView):
    permission_classes = (IsAuthenticated, IsAdmin)

    def get(self, request, format=None):
        start_date, end_date = dry(request)
        takeout_orders = Order.objects.filter(
            order_type='with',
            status='completed',
            created_at__range=(start_date, end_date)
        ).count()

        delivery_orders = Order.objects.filter(
            order_type='delivery',
            status='completed',
            created_at__range=(start_date, end_date)
        ).count()

        return Response({'takeout_orders': takeout_orders, 'delivery_orders': delivery_orders},
                        status=status.HTTP_200_OK)


class PaymentMethodsStatsAPIView(APIView):
    permission_classes = (IsAuthenticated, IsAdmin)

    def get(self, request, format=None):
        start_date, end_date = dry(request)
        stats = Order.objects.filter(
            status='completed',
            created_at__range=(start_date, end_date)
        ).values('pay_type').annotate(
            count=Count('id'),
            total_amount=Sum('full_price')
        ).order_by('-total_amount')

        return Response(stats, status=status.HTTP_200_OK)


class PopularCategoriesStatsAPIView(APIView):
    permission_classes = (IsAuthenticated, IsAdmin)

    def get(self, request, format=None):
        start_date, end_date = dry(request)
        stats = OrderItem.objects.filter(
            order__status='completed',
            order__created_at__range=(start_date, end_date)
        ).values('food__category').annotate(
            count=Sum('quantity'),
            total_amount=Sum('price')
        ).order_by('-total_amount')
        return Response(stats, status=status.HTTP_200_OK)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    http_method_names = ['get', 'post', 'put', 'patch']
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderDetailSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.validated_data['user'] = request.user
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        order_status = request.query_params.get('status', None)
        if order_status:
            orders = Order.objects.filter(status=order_status).all()
        else:
            orders = Order.objects.all()
        page = self.paginate_queryset(orders)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
