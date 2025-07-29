import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter
from Django_LoveSync_Diary.code.DjangoPro1.App.routing import websocket_urlpatterns

# 修正环境变量设置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoPro1.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # 处理HTTP请求
    "websocket": websocket_urlpatterns,  # 处理WebSocket请求
})