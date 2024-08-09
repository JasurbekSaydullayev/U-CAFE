from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import UserViewSet, GetUserInfo, ChangePassword, ChangePasswordEmployeesForSuperAdmins, UploadPhotoUser, \
    EditUserInfo, EditUserInfoForSuperAdminOrManager, DeletePhotoUser

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = router.urls

urlpatterns += [
    path('get-user-info/', GetUserInfo.as_view(), name='get-user-info'),
    path('change-password/', ChangePassword.as_view(), name='change-password'),
    path('user/change-password/', ChangePasswordEmployeesForSuperAdmins.as_view(), name='users-change-password'),
    path('upload-image/', UploadPhotoUser.as_view(), name='upload-image'),
    path('delete-image/', DeletePhotoUser.as_view(), name='upload-image'),
    path('edit-user-info/', EditUserInfo.as_view(), name='edit-user-info'),
    path('users/edit-user-info/<int:pk>/', EditUserInfoForSuperAdminOrManager.as_view(),
         name='users-edit-user-info'),
]
