from datetime import datetime

import requests
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Count

from orders.DRY import dry
from pagination import StandardResultsSetPagination
from permissions import IsAdmin
from .serializers import OrderSerializer, OrderDetailSerializer
from orders.models import Order, OrderItem
from expenses.models import Expenses

manual_parameters = [
    openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, format='date',
                      description='Start date in YYYY-MM-DD format'),
    openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, format='date',
                      description='End date in YYYY-MM-DD format'),
]


# Statistics
class IncomeAPIView(APIView):
    permission_classes = (IsAuthenticated, IsAdmin)

    @swagger_auto_schema(manual_parameters=manual_parameters)
    def get(self, request, format=None):
        start_date, end_date = dry(request)
        total_income = Order.objects.filter(
            status='completed',
            created_at__range=(start_date, end_date)
        ).aggregate(total_income=Sum('full_price'))['total_income'] or 0
        return Response({'total_income': total_income}, status=status.HTTP_200_OK)


class ExpensesAPIView(APIView):
    permission_classes = (IsAuthenticated, IsAdmin)

    @swagger_auto_schema(manual_parameters=manual_parameters)
    def get(self, request, format=None):
        start_date, end_date = dry(request)
        total_expenses = Expenses.objects.filter(
            date__range=(start_date, end_date)
        ).aggregate(total_expenses=Sum('price'))['total_expenses'] or 0

        return Response({'total_expenses': total_expenses}, status=status.HTTP_200_OK)


class SalesAPIView(APIView):
    permission_classes = (IsAuthenticated, IsAdmin)

    @swagger_auto_schema(manual_parameters=manual_parameters)
    def get(self, request, format=None):
        start_date, end_date = dry(request)
        total_sales = Order.objects.filter(
            status='completed',
            created_at__range=(start_date, end_date)
        ).count()

        return Response({'total_sales': total_sales}, status=status.HTTP_200_OK)


class OrdersAPIView(APIView):
    permission_classes = (IsAuthenticated, IsAdmin)

    @swagger_auto_schema(manual_parameters=manual_parameters)
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

    @swagger_auto_schema(manual_parameters=manual_parameters)
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

    @swagger_auto_schema(
        manual_parameters=manual_parameters)
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
        status_pay = request.query_params.get('status_pay', None)
        today = datetime.today().date()
        orders = Order.objects.filter(created_at__date=today).order_by('-created_at')
        if order_status:
            orders = orders.filter(status=order_status)
        if status_pay:
            orders = orders.filter(status_pay=status_pay)
        page = self.paginate_queryset(orders)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)


class GetHistoryOrders(APIView):
    serializer_class = OrderSerializer
    pagination_class = StandardResultsSetPagination

    @swagger_auto_schema(
        manual_parameters=[
                              openapi.Parameter('page', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                                                description='Page number'),
                              openapi.Parameter('page_size', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                                                description='Number of results per page'),
                              openapi.Parameter('order_type', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                                                description='Types are:  delivery, with, there'),
                              openapi.Parameter('pay_type', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                                                description='Types are: cash, payme, click, terminal')
                          ] + manual_parameters
    )
    def get(self, request, format=None):
        start_date, end_date = dry(request)
        order_type = request.query_params.get('order_type', None)
        pay_type = request.query_params.get('pay_type', None)
        orders = Order.objects.filter(
            status='completed',
            created_at__range=(start_date, end_date)
        ).order_by('-created_at')
        if order_type:
            orders = orders.filter(order_type=order_type)
        if pay_type:
            orders = orders.filter(pay_type=pay_type)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(orders, request)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = self.serializer_class(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
