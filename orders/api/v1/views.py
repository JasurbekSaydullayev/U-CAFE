import requests
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Count

from .DRY import dry
from .serializers import OrderItemSerializer, OrderSerializer, OrderDetailSerializer
from .permissions import IsSuperAdminOrOwner
from orders.models import Order, OrderItem
from expenses.models import Expenses

from django.db.models.signals import post_save
from django.dispatch import receiver


def send_order_status_webhook(order):
    if order.webhook_url:
        data = {
            'order_id': order.id,
            'status': order.status,
            'status_pay': order.status_pay,
            'full_price': order.full_price
        }
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(order.webhook_url, json=data, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error sending webhook: {e}")


@receiver(post_save, sender=Order)
def order_status_updated(sender, instance, **kwargs):
    send_order_status_webhook(instance)


# Statistics
class IncomeAPIView(APIView):
    def get(self, request, format=None):
        start_date, end_date = dry(request)
        total_income = Order.objects.filter(
            status='completed',
            created_at__range=(start_date, end_date)
        ).aggregate(total_income=Sum('full_price'))['total_income'] or 0
        return Response({'total_income': total_income}, status=status.HTTP_200_OK)


class ExpensesAPIView(APIView):
    def get(self, request, format=None):
        start_date, end_date = dry(request)
        total_expenses = Expenses.objects.filter(
            date__range=(start_date, end_date)
        ).aggregate(total_expenses=Sum('price'))['total_expenses'] or 0

        return Response({'total_expenses': total_expenses}, status=status.HTTP_200_OK)


class SalesAPIView(APIView):
    def get(self, request, format=None):
        start_date, end_date = dry(request)
        total_sales = Order.objects.filter(
            status='completed',
            created_at__range=(start_date, end_date)
        ).count()

        return Response({'total_sales': total_sales}, status=status.HTTP_200_OK)


class OrdersAPIView(APIView):
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


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    http_method_names = ['get', 'post', 'put', 'patch']

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
