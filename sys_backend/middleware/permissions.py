"""
权限中间件 - 专门处理管理系统的权限控制
"""
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
import jwt
from django.conf import settings


class AdminPermissionMiddleware(MiddlewareMixin):
    """管理员权限中间件"""
    
    def process_request(self, request):
        """处理请求前的权限检查"""
        # 只检查管理员相关的API路径
        if not request.path.startswith('/admin-api/'):
            return None
        
        # 允许登录和注册接口通过
        if request.path.startswith('/admin-api/user/auth/login/') or request.path.startswith('/admin-api/user/auth/register/'):
            return None
            
        # 获取JWT token
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return JsonResponse({
                'code': 401,
                'message': '未提供认证信息'
            }, status=401)
        
        token = auth_header.split(' ')[1]
        
        try:
            # 验证JWT token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            if not user_id:
                return JsonResponse({
                    'code': 401,
                    'message': '无效的认证信息'
                }, status=401)
            
            # 获取用户信息
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            try:
                user = User.objects.get(id=user_id)
                request.user = user
                request.user_id = user_id
                
                # 检查管理员权限
                if not (user.is_staff or user.is_superuser):
                    return JsonResponse({
                        'code': 403,
                        'message': '权限不足，需要管理员权限'
                    }, status=403)
                
            except User.DoesNotExist:
                return JsonResponse({
                    'code': 401,
                    'message': '用户不存在'
                }, status=401)
                
        except jwt.ExpiredSignatureError:
            return JsonResponse({
                'code': 401,
                'message': '认证信息已过期'
            }, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({
                'code': 401,
                'message': '无效的认证信息'
            }, status=401)
        
        return None


class PublicPermissionMiddleware(MiddlewareMixin):
    """公开API权限中间件 - 用于用户举报等公开功能"""
    
    def process_request(self, request):
        """处理公开API请求的权限检查"""
        # 只检查公开API路径
        if not request.path.startswith('/admin-api/community/reports/create_public/'):
            return None
            
        # 获取JWT token（可选）
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            try:
                # 验证JWT token
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                user_id = payload.get('user_id')
                
                if user_id:
                    try:
                        from django.contrib.auth import get_user_model
                        User = get_user_model()
                        user = User.objects.get(id=user_id)
                        request.user = user
                        request.user_id = user_id
                    except User.DoesNotExist:
                        pass
                        
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                # token无效时，继续处理但用户未认证
                pass
        
        return None


class SQLPermissionMiddleware(MiddlewareMixin):
    """SQL操作权限中间件 - 确保只有管理员可以执行管理SQL操作"""
    
    def process_request(self, request):
        """处理SQL操作权限检查"""
        # 只检查管理员相关的API路径
        if not request.path.startswith('/admin-api/'):
            return None
        
        # 如果用户已经通过JWT认证，跳过额外检查
        if hasattr(request, 'user') and request.user.is_authenticated:
            return None
        
        # 检查是否有特殊的管理员token
        admin_token = request.META.get('HTTP_X_ADMIN_TOKEN')
        if admin_token and admin_token == settings.ADMIN_API_TOKEN:
            return None
        
        return JsonResponse({
            'code': 403,
            'message': '需要管理员权限'
        }, status=403)