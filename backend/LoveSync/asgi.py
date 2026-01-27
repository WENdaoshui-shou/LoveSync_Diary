import os

# 先设置环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LoveSync.settings')

# 加载Django应用
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

# 现在再导入其他模块
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import collab.routing  # 导入你的websocket路由

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # WebSocket路由（带身份认证）
    "websocket": AuthMiddlewareStack(
        URLRouter(
            collab.routing.websocket_urlpatterns
        )
    ),
})