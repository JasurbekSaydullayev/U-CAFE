from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    IncomeAPIView, ExpensesAPIView, SalesAPIView, OrdersAPIView,
    PaymentMethodsStatsAPIView, PopularCategoriesStatsAPIView, OrderViewSet, GetHistoryOrders, SalesReportView,
    SalesByDayOfWeekAPIView, CancelOrder
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
    path('get-history-orders/', GetHistoryOrders.as_view(), name='get-history-orders'),
    path('statistics/sales-foods/', SalesReportView.as_view(), name='sales-foods'),
    path('statistics/sales-by-day-week/', SalesByDayOfWeekAPIView.as_view(), name='sales-by-day-week'),
    path('cancel-order/<int:pk>/', CancelOrder.as_view(), name='cancel-order'),

]

urlpatterns += router.urls
