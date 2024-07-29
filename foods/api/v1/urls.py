from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import FoodViewSet

router = DefaultRouter()
router.register('foods', FoodViewSet, basename='foods')

urlpatterns = router.urls
