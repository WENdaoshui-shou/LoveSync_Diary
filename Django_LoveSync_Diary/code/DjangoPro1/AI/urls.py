# -*- coding: utf-8 -*-
# @Time        :2025/8/7 17:56
# @Author      :文刀水寿
# @File        : urls.py
"""
 @Description :
"""
from .views import *
from django.urls import path

urlpatterns = [
    path('api/lovesync/', lovesync_index, name='loveync-AI'),
    path('api/chat/init/', ChatInitView, name='chat-init'),
    path('api/chat/message/', ChatMessageView, name='chat-message'),
    path('api/chat/status/<str:session_id>/', get_ai_response, name='chat-status'),
]
