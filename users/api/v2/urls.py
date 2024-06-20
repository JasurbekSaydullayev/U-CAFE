from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import UserViewSet, UserConfirmWithCodeViewSet

router = DefaultRouter()

router.register('users', UserViewSet, basename='users')
router.register('user-confirm', UserConfirmWithCodeViewSet, basename='user-confirm')

urlpatterns = router.urls
