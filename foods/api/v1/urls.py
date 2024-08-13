from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import FoodViewSet, DeletePhotoFood

router = DefaultRouter()
router.register('foods', FoodViewSet, basename='foods')

urlpatterns = router.urls

urlpatterns += [
    path('delete-image-food/<int:pk>/', DeletePhotoFood.as_view(), name='delete-image-food'),
]
