from datetime import datetime

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db.models import Sum, Count, F

from foods.models import Food
from orders.DRY import dry
from pagination import StandardResultsSetPagination
from permissions import IsAdmin, IsSeller, IsManager
from .serializers import OrderSerializer, OrderDetailSerializer, SalesReportSerializer
from orders.models import Order, OrderItem, OrderPayments
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

        total_income = OrderPayments.objects.filter(
            order__status='completed',
            order__created_at__range=(start_date, end_date)
        ).aggregate(total_income=Sum('price'))['total_income'] or 0

        total_trade = Order.objects.filter(
            status='completed',
            created_at__range=(start_date, end_date)
        ).aggregate(total_trade=Sum('full_price'))['total_trade'] or 0

        previous_total_trade = Order.objects.filter(
            status='completed',
            created_at__range=(previous_start_date, previous_end_date)
        ).aggregate(previous_total_trade=Sum('full_price'))['previous_total_trade'] or 0

        previous_total_income = OrderPayments.objects.filter(
            order__status='completed',
            order__created_at__range=(previous_start_date, previous_end_date)
        ).aggregate(previous_total_income=Sum('price'))['previous_total_income'] or 0

        if previous_total_trade:
            percentage_change_trade = ((total_trade - previous_total_trade) / previous_total_trade) * 100
        else:
            percentage_change_trade = None

        if previous_total_income:
            percentage_change_income = ((total_income - previous_total_income) / previous_total_income) * 100
        else:
            percentage_change_income = None

        return Response({
            'total_income': total_income,
            'percentage_change_income': percentage_change_income,
            'total_trade': total_trade,
            'percentage_change_trade': percentage_change_trade,
        }, status=status.HTTP_200_OK)


class GetDiscountOrders(APIView):
    permission_classes = (IsAuthenticated, IsAdmin)
    serializer_class = OrderDetailSerializer

    @swagger_auto_schema(
        manual_parameters=manual_parameters + [
            openapi.Parameter('page', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Page number'),
            openapi.Parameter('page_size', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Number of results per page'), ])
    def get(self, request, format=None):
        start_date, end_date, previous_start_date, previous_end_date = dry(request)
        discount_orders = Order.objects.filter(discount__gt=0, created_at__range=(start_date, end_date)).order_by(
            'created_at')
        serializer = self.serializer_class(discount_orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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

        payments = OrderPayments.objects.filter(
            order__status='completed',
            order__created_at__range=(start_date, end_date)
        ).values('pay_type').annotate(
            count=Count('id'),
            total_amount=Sum('price')
        ).order_by('-total_amount')

        total_payments = OrderPayments.objects.filter(
            order__status='completed',
            order__created_at__range=(start_date, end_date)
        ).aggregate(total_count=Count('id'))['total_count'] or 0

        payment_dict = {payment['pay_type']: payment for payment in payments}

        pay_type_choices = dict(OrderPayments._meta.get_field('pay_type').choices)

        results = []
        for pay_type, _ in pay_type_choices.items():
            if pay_type in payment_dict:
                count = payment_dict[pay_type]['count']
                total_amount = payment_dict[pay_type]['total_amount']
            else:
                count = 0
                total_amount = 0
            percentage = (count / total_payments) * 100 if total_payments > 0 else 0
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
    permission_classes = [IsSeller]

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

    def partial_update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if instance.status == 'new':
            if instance.status_pay == 'unpaid' and serializer.validated_data['status_pay'] == 'unpaid':
                return Response({"message": "Iltimos avval to'lovni amalga oshiring"},
                                status=status.HTTP_400_BAD_REQUEST)
            items_data = serializer.validated_data.pop('items', None)
            payments_data = serializer.validated_data.pop('payments', None)
            validated_data = serializer.validated_data
            instance.status = validated_data.get('status', instance.status)
            instance.order_type = validated_data.get('order_type', instance.order_type)
            instance.status_pay = validated_data.get('status_pay', instance.status_pay)
            instance.position = validated_data.get('position', instance.position)
            instance.save()
            if items_data:
                for item_data in items_data:
                    food = item_data.get('food')
                    quantity = item_data.get('quantity')
                    existing_item = instance.items.filter(food=food).first()
                    if existing_item:
                        quantity_diff = quantity - existing_item.quantity
                        if quantity_diff == 0:
                            continue
                        elif quantity_diff > 0:
                            if food.count < quantity_diff:
                                return Response(
                                    {"status": False, 'msg': f"{food.name} ovqatdan yetarli miqdor yo'q"},
                                    status=status.HTTP_400_BAD_REQUEST
                                )
                            food.count -= quantity_diff
                        else:
                            food.count += abs(quantity_diff)
                        food.save()
                        existing_item.quantity = quantity
                        existing_item.price = food.price * quantity
                        existing_item.save()
                    else:
                        if food.count < quantity:
                            return Response(
                                {"status": False, 'msg': f"{food.name} ovqatdan yetarli miqdor yo'q"},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        food.count -= quantity
                        food.save()
                        OrderItem.objects.create(order=instance, food=food, quantity=quantity,
                                                 price=food.price * quantity)
                instance.items.filter(quantity=0).delete()
                if instance.items.count() == 0:
                    instance.delete()
                    return Response({"status": "True", 'msg': "Buyurtma bekor qilindi"}, status=status.HTTP_200_OK)
                instance.position = instance.items.all().count()
                instance.full_price = instance.items.aggregate(total=Sum('price'))['total']
                instance.save()
            if payments_data:
                total_payment = sum(payment['price'] for payment in payments_data)
                if total_payment > instance.full_price:
                    return Response({"status": False, 'msg': "To'lov summasi buyurtma summasidan oshib ketmoqda."},
                                    status=status.HTTP_400_BAD_REQUEST)
                for payment_data in payments_data:
                    pay_type = payment_data.get('pay_type')
                    price = payment_data.get('price')
                    existing_payment = instance.payments.filter(pay_type=pay_type).first()
                    if existing_payment:
                        if price == 0:
                            existing_payment.delete()
                        else:
                            existing_payment.price = price
                            existing_payment.save()
                    else:
                        if price == 0:
                            continue
                        OrderPayments.objects.create(order=instance, **payment_data)
                instance.discount = instance.full_price - total_payment
                instance.save()
            return Response(serializer.data)
        elif instance.status == 'processing':
            order_status = request.data.get('status', instance.status)
            if order_status != 'completed':
                return Response({"message": "Ushbu buyurtma statusini faqat 'completed' ga o'zgartirish mumkin"},
                                status=status.HTTP_400_BAD_REQUEST)
            instance.status = order_status
            instance.save()
            return Response({"message": "Status completedga o'zgartirildi"}, status=status.HTTP_200_OK)
        elif instance.status == 'completed':
            return Response({"message": "Ushbu buyurtmani o'zgartirish mumkin emas"},
                            status=status.HTTP_400_BAD_REQUEST)


class GetHistoryOrders(APIView):
    serializer_class = OrderSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsManager]

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
    permission_classes = [IsAuthenticated, IsAdmin]

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


class CancelOrder(APIView):
    permission_classes = [IsManager]

    #
    def post(self, request, *args, **kwargs):
        order = Order.objects.filter(id=kwargs['pk']).first()
        if order:
            order.status = 'cancelled'
            order.save()
            return Response({"message": "Buyurtma bekor qilindi"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Buyurtma topilmadi"}, status=status.HTTP_404_NOT_FOUND)


class GetCancelledOrders(APIView):
    permission_classes = [IsManager]
    serializer_class = OrderSerializer
    pagination_class = StandardResultsSetPagination

    @swagger_auto_schema(
        manual_parameters=manual_parameters + [
            openapi.Parameter('page', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Page number'),
            openapi.Parameter('page_size', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Number of results per page'), ])
    def get(self, request, *args, **kwargs):
        start_date, end_date, previous_start_date, previous_end_date = dry(request)
        orders = Order.objects.filter(status='cancelled',
                                      created_at__range=(start_date, end_date)).all().order_by(
            '-created_at')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(orders, request)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)
