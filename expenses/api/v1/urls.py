from django.urls import path

from .views import ExpenseViewSet

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('expenses', ExpenseViewSet, basename='expenses')

urlpatterns = router.urls
