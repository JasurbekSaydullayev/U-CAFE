from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import FoodViewSet, PhotoViewSet

router = DefaultRouter()
router.register('foods', FoodViewSet, basename='foods')
router.register('photo-foods', PhotoViewSet, basename='photo-foods')

urlpatterns = router.urls
