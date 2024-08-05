from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import UserViewSet, GetUserInfo

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = router.urls

urlpatterns += [
    path('get-user-info/', GetUserInfo.as_view(), name='get-user-info'),
]
