from django.urls import path
from . import views

app_name = 'message'  # URL命名空间

urlpatterns = [
    path('', views.message_list, name='list'),  # 消息列表

    path('update-status/', views.update_message_status, name='update_status'),  # 更新消息状态
    path('unread-count/', views.get_unread_count, name='unread_count'),  # 获取未读数量
    path('send-private/', views.send_private_message, name='send_private_message'),  # 发送私信
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),  # 全部标记已读

    path('private-chat/<int:user_id>/', views.private_chat_detail, name='private_chat_detail'),  # 私信对话详情
]
