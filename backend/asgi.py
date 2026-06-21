import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

from django.core.asgi import get_asgi_application

django_asgi_app= get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from rent.routing import websocket_urlpatterns
from rent.middleware import JWTAuthMiddleware
from channels.security.websocket import AllowedHostsOriginValidator

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(JWTAuthMiddleware(URLRouter(websocket_urlpatterns))),
})
