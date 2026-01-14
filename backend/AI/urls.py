# -*- coding: utf-8 -*-
# @Time        :2025/8/7 17:56
# @Author      :文刀水寿
# @File        : urls.py
"""
 @Description : AI应用URL配置
"""
from django.urls import path
from .views import lovesync_index, ChatInitView, ChatMessageView

app_name = 'ai'

urlpatterns = [
    path('lovesync/', lovesync_index, name='loveync-AI'),
    path('chat/init/', ChatInitView, name='chat-init'),
    path('chat/message/', ChatMessageView, name='chat-message'),
]
