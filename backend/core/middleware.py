from channels.middleware import BaseMiddleware
from asgiref.sync import sync_to_async
from urllib.parse import parse_qs
import logging

logger = logging.getLogger(__name__)

# 延迟导入，避免循环导入
def lazy_import():
    global User, AccessToken, InvalidToken, TokenError
    from rest_framework_simplejwt.tokens import AccessToken
    from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
    from django.contrib.auth import get_user_model
    User = get_user_model()

@sync_to_async
def get_user(token):
    """异步解析 Token 并获取用户"""
    lazy_import()
    if not token:
        logger.warning("Token 为空")
        return None
    
    try:
        at = AccessToken(token)
        user_id = at.get("user_id")
        if not user_id:
            logger.warning("Token 无 user_id")
            return None
        
        # 查询自定义用户模型
        user = User.objects.get(id=user_id)
        logger.info(f"✅ 用户认证成功：{user.username}（ID: {user_id}）")
        return user
    
    except (InvalidToken, TokenError) as e:
        logger.error(f"❌ Token 无效：{str(e)}")
        return None
    except User.DoesNotExist:
        logger.error(f"❌ 用户 ID {user_id} 不存在")
        return None
    except Exception as e:
        logger.error(f"❌ 认证中间件错误：{str(e)}", exc_info=True)
        return None

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # 解析 URL 中的 Token
        query_string = scope.get("query_string", b"").decode("utf-8")
        params = parse_qs(query_string)
        token = params.get("token", [None])[0]
        
        # 获取用户并设置到 scope
        scope["user"] = await get_user(token)
        
        # 无用户则返回认证失败
        if not scope["user"] or not scope["user"].is_authenticated:
            await send({
                "type": "websocket.close",
                "code": 4001,
                "reason": "Authentication required"
            })
            return
        
        # 认证通过，继续处理
        return await super().__call__(scope, receive, send)

def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(inner)