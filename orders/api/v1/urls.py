from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    IncomeAPIView, ExpensesAPIView, SalesAPIView, OrdersAPIView,
    PaymentMethodsStatsAPIView, PopularCategoriesStatsAPIView, OrderViewSet
)

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='orders')

urlpatterns = [
    path('statistics/income/', IncomeAPIView.as_view(), name='income-stats'),
    path('statistics/expenses/', ExpensesAPIView.as_view(), name='expenses-stats'),
    path('statistics/sales/', SalesAPIView.as_view(), name='sales-stats'),
    path('statistics/orders/', OrdersAPIView.as_view(), name='orders-stats'),
    path('statistics/payment-methods/', PaymentMethodsStatsAPIView.as_view(), name='payment-methods-stats'),
    path('statistics/popular-categories/', PopularCategoriesStatsAPIView.as_view(), name='popular-categories-stats'),
]

urlpatterns += router.urls
