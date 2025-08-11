import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from App.routing import websocket_urlpatterns


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoPro1.settings')
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket":
        URLRouter(
            websocket_urlpatterns
        ),
})
