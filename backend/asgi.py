import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from rent.routing import websocket_urlpatterns
from rent.middleware import JWTAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django_asgi_app= get_asgi_application()
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JWTAuthMiddleware(URLRouter(websocket_urlpatterns)) # from middleware.py for custom authentication
})
# import os
# from channels.routing import ProtocolTypeRouter
# from django.core.asgi import get_asgi_application

# os.environ.setdefault(
#     "DJANGO_SETTINGS_MODULE",
#     "backend.settings"
# )
# django_asgi_app= get_asgi_application()
# application = ProtocolTypeRouter({
#     "http": django_asgi_app,
# })