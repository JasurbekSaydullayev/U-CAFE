import os
import django
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ucafe.settings')

django.setup()

django_asgi_app = get_asgi_application()

from orders import routing
from orders.middleware import JsonTokenAuthMiddlewareStack  # Убедитесь, что путь правильный

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JsonTokenAuthMiddlewareStack(
        AuthMiddlewareStack(
            URLRouter(
                routing.websocket_urlpatterns
            )
        )
    ),
})
