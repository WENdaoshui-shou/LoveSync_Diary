from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import check_password

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """管理员登录"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({
            'success': False,
            'message': '用户名和密码不能为空'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 验证用户
    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response({
            'success': False,
            'message': '用户名或密码错误'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # 检查是否是管理员
    if not user.is_staff:
        return Response({
            'success': False,
            'message': '非管理员用户无法登录后台'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # 生成JWT token
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'success': True,
        'message': '登录成功',
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser
        }
    })


@api_view(['GET'])
def user_info_view(request):
    """获取当前用户信息"""
    user = request.user
    
    return Response({
        'success': True,
        'data': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M:%S') if user.date_joined else None,
            'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None
        }
    })


@api_view(['POST'])
def refresh_token_view(request):
    """刷新token"""
    refresh_token = request.data.get('refresh')
    
    if not refresh_token:
        return Response({
            'success': False,
            'message': 'refresh token不能为空'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        refresh = RefreshToken(refresh_token)
        return Response({
            'success': True,
            'access': str(refresh.access_token)
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': 'token无效或已过期'
        }, status=status.HTTP_401_UNAUTHORIZED)