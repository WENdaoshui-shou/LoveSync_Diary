# -*- coding: utf-8 -*-
# @Time        :2025/7/29 10:41
# @Author      :文刀水寿
# @File        : routing.py.py
"""
 @Description :
"""
from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/collaboration/new/$', consumers.CollaborationConsumer.as_asgi()),
    re_path(r'ws/collaboration/(?P<document_id>\w+)/$', consumers.CollaborationConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})