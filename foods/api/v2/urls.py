from rest_framework.routers import DefaultRouter

from .views import FoodViewSetV2

router = DefaultRouter()
router.register('foods', FoodViewSetV2, basename='foods')

urlpatterns = router.urls
