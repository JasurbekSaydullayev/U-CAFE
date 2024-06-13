from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="U Cafe",
        default_version='v1', ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    # v1
    path('api/v1/', include('users.api.v1.urls')),
    path('api/v1/', include('foods.api.v1.urls')),
    path('api/v1/', include('orders.api.v1.urls')),
    path('api/v1/', include('expenses.api.v1.urls')),
    path('api/v1/', include('complaints.api.v1.urls')),

    # v2
    path('api/v2/', include('complaints.api.v2.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
