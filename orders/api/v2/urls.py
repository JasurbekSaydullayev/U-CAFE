from rest_framework.routers import DefaultRouter

from orders.api.v2.views import OrderViewSetV2

router = DefaultRouter()
router.register(r'orders', OrderViewSetV2, basename='orders')

urlpatterns = router.urls
