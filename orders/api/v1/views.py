from datetime import datetime

import requests
from django.core.cache import cache
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Count, F

from foods.models import Food
from orders.DRY import dry
from pagination import StandardResultsSetPagination
from permissions import IsAdmin
from .serializers import OrderSerializer, OrderDetailSerializer, SalesReportSerializer
from orders.models import Order, OrderItem
from expenses.models import Expenses

manual_parameters = [
    openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, format='date',
                      description='Start date in YYYY-MM-DD format'),
    openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, format='date',
                      description='End date in YYYY-MM-DD format'),
]


class IncomeAPIView(APIView):
    permission_classes = (IsAuthenticated, IsAdmin)

    @swagger_auto_schema(manual_parameters=manual_parameters)
    def get(self, request, format=None):
        start_date, end_date, previous_start_date, previous_end_date = dry(request)

        total_income = Order.objects.filter(
            status='completed',
            created_at__range=(start_date, end_date)
        ).aggregate(total_income=Sum('full_price'))['total_income'] or 0

        previous_total_income = Order.objects.filter(
            status='completed',
            created_at__range=(previous_start_date, previous_end_date)
        ).aggregate(previous_total_income=Sum('full_price'))['previous_total_income'] or 0

        if previous_total_income:
            percentage_change = ((total_income - previous_total_income) / previous_total_income) * 100
        else:
            percentage_change = None

        return Response({
            'total_income': total_income,
            'percentage_change': percentage_change
        }, status=status.HTTP_200_OK)


class ExpensesAPIView(APIView):
    permission_classes = (IsAuthenticated, IsAdmin)

    @swagger_auto_schema(manual_parameters=manual_parameters)
    def get(self, request, format=None):
        start_date, end_date, previous_start_date, previous_end_date = dry(request)

        total_expenses = Expenses.objects.filter(
            date__range=(start_date, end_date)
        ).aggregate(total_expenses=Sum('price'))['total_expenses'] or 0

        previous_total_expenses = Expenses.objects.filter(
            date__range=(previous_start_date, previous_end_date)
        ).aggregate(total_expenses=Sum('price'))['total_expenses'] or 0

        if previous_total_expenses:
            percentage_change = ((total_expenses - previous_total_expenses) / previous_total_expenses) * 100
        else:
            percentage_change = None

        return Response({
            'total_expenses': total_expenses,
            'percentage_change': percentage_change
        }, status=status.HTTP_200_OK)


class SalesAPIView(APIView):
    permission_classes = (IsAuthenticated, IsAdmin)

    @swagger_auto_schema(manual_parameters=manual_parameters)
    def get(self, request, format=None):
        start_date, end_date, previous_start_date, previous_end_date = dry(request)

        total_sales = Order.objects.filter(
            status='completed',
            created_at__range=(start_date, end_date)
        ).count()

        previous_total_sales = Order.objects.filter(
            status='completed',
            created_at__range=(previous_start_date, previous_end_date)
        ).count()

        if previous_total_sales:
            percentage_change = ((total_sales - previous_total_sales) / previous_total_sales) * 100
        else:
            percentage_change = None

        return Response({
            'total_sales': total_sales,
            'percentage_change': percentage_change
        }, status=status.HTTP_200_OK)


class OrdersAPIView(APIView):
    permission_classes = (IsAuthenticated, IsAdmin)

    @swagger_auto_schema(manual_parameters=manual_parameters)
    def get(self, request, format=None):
        start_date, end_date, previous_start_date, previous_end_date = dry(request)

        takeout_orders = Order.objects.filter(
            order_type='with',
            status='completed',
            created_at__range=(start_date, end_date)
        ).count()

        previous_takeout_orders = Order.objects.filter(
            order_type='with',
            status='completed',
            created_at__range=(previous_start_date, previous_end_date)
        ).count()

        delivery_orders = Order.objects.filter(
            order_type='delivery',
            status='completed',
            created_at__range=(start_date, end_date)
        ).count()

        previous_delivery_orders = Order.objects.filter(
            order_type='delivery',
            status='completed',
            created_at__range=(previous_start_date, previous_end_date)
        ).count()

        if previous_takeout_orders:
            takeout_percentage_change = ((takeout_orders - previous_takeout_orders) / previous_takeout_orders) * 100
        else:
            takeout_percentage_change = None

        if previous_delivery_orders:
            delivery_percentage_change = ((delivery_orders - previous_delivery_orders) / previous_delivery_orders) * 100
        else:
            delivery_percentage_change = None

        return Response({
            'takeout_orders': takeout_orders,
            'takeout_percentage_change': takeout_percentage_change,
            'delivery_orders': delivery_orders,
            'delivery_percentage_change': delivery_percentage_change
        }, status=status.HTTP_200_OK)


class PaymentMethodsStatsAPIView(APIView):
    permission_classes = (IsAuthenticated, IsAdmin)

    @swagger_auto_schema(manual_parameters=manual_parameters)
    def get(self, request, format=None):
        start_date, end_date, previous_start_date, previous_end_date = dry(request)

        orders = Order.objects.filter(
            status='completed',
            created_at__range=(start_date, end_date)
        ).values('pay_type').annotate(
            count=Count('id'),
            total_amount=Sum('full_price')
        ).order_by('-total_amount')

        total_orders = Order.objects.filter(
            status='completed',
            created_at__range=(start_date, end_date)
        ).count()

        order_dict = {order['pay_type']: order for order in orders}

        results = []
        for pay_type_choice in Order._meta.get_field('pay_type').choices:
            pay_type = pay_type_choice[0]
            if pay_type in order_dict:
                count = order_dict[pay_type]['count']
                total_amount = order_dict[pay_type]['total_amount']
            else:
                count = 0
                total_amount = 0
            percentage = (count / total_orders) * 100 if total_orders > 0 else 0
            results.append({
                'pay_type': pay_type,
                'count': count,
                'total_amount': total_amount,
                'percentage': percentage
            })

        return Response(results)


class PopularCategoriesStatsAPIView(APIView):
    permission_classes = (IsAuthenticated, IsAdmin)

    @swagger_auto_schema(manual_parameters=manual_parameters)
    def get(self, request, format=None):
        start_date, end_date, previous_start_date, previous_end_date = dry(request)

        category_stats = OrderItem.objects.filter(
            order__status='completed',
            order__created_at__range=(start_date, end_date)
        ).values('food__category').annotate(
            count=Sum('quantity'),
            total_amount=Sum('price')
        ).order_by('-total_amount')

        total_quantity = sum(category['count'] for category in category_stats)
        total_amount = sum(category['total_amount'] for category in category_stats)

        category_dict = {category['food__category']: category for category in category_stats}

        results = []
        for category_choice in Food._meta.get_field('category').choices:
            category_name = category_choice[0]
            if category_name in category_dict:
                count = category_dict[category_name]['count']
                amount = category_dict[category_name]['total_amount']
            else:
                count = 0
                amount = 0
            percentage_quantity = round((count / total_quantity) * 100, 1) if total_quantity > 0 else 0
            results.append({
                'category': category_name,
                'count': count,
                'total_amount': amount,
                'percentage_quantity': percentage_quantity,
            })

        return Response(results, status=status.HTTP_200_OK)


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

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('status_pay', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                          description='Enter status pay, paid or unpaid'), ])
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
        start_date, end_date, previous_start_date, previous_end_date = dry(request)
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


class SalesReportView(APIView):
    pagination_class = StandardResultsSetPagination
    serializer_class = SalesReportSerializer

    @swagger_auto_schema(
        manual_parameters=manual_parameters + [
            openapi.Parameter('page', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Page number'),
            openapi.Parameter('page_size', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Number of results per page')])
    def get(self, request):
        sales_data = OrderItem.objects.values(
            'food__name',
            'food__category',
            'food__price'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_sales=Sum(F('quantity') * F('food__price'))
        ).order_by('-quantity')

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(sales_data, request)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = self.serializer_class(sales_data, many=True)
        return Response(serializer.data)


class SalesByDayOfWeekAPIView(APIView):
    permission_classes = (IsAuthenticated, IsAdmin)

    @swagger_auto_schema(manual_parameters=manual_parameters)
    def get(self, request, format=None):
        # sales_data = cache.get('sales_by_day')
        # if sales_data is None:
        start_date, end_date, previous_start_date, previous_end_date = dry(request)

        days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        sales_data = {day: {'takeout': 0, 'delivery': 0} for day in days_of_week}

        orders = Order.objects.filter(
            status='completed',
            created_at__range=(start_date, end_date)
        ).values('created_at', 'order_type')

        for order in orders:
            day_of_week = order['created_at'].strftime('%A').lower()
            if day_of_week in sales_data:
                if order['order_type'] == 'with':
                    sales_data[day_of_week]['takeout'] += 1
                elif order['order_type'] == 'delivery':
                    sales_data[day_of_week]['delivery'] += 1
            # cache.set('sales_by_day', sales_data, timeout=300)
        #
        return Response(sales_data, status=status.HTTP_200_OK)
