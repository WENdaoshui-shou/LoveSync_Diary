from django.urls import path
from collab.consumers import DiarySyncConsumer

websocket_urlpatterns = [
    path('ws/diary/sync/', DiarySyncConsumer.as_asgi()),
]