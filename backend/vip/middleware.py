from django.utils.deprecation import MiddlewareMixin
from core.models import VIPMember

class VIPStatusCheckMiddleware(MiddlewareMixin):
    """VIP状态检查中间件，在每个请求中检查用户的VIP状态"""
    
    def process_request(self, request):
        # 只有已登录用户才需要检查VIP状态
        if request.user.is_authenticated:
            try:
                # 检查用户是否有VIP记录
                if hasattr(request.user, 'vip'):
                    vip = request.user.vip
                    # 调用VIP模型的check_vip_status方法检查状态
                    vip.check_vip_status()
            except Exception as e:
                # 记录错误，但不影响请求处理
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'VIP状态检查失败: {e}')
        
        return None
