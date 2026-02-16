from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet
from .auth_views import login_view, user_info_view, refresh_token_view

app_name = 'user_manage'

# API路由
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    # 认证相关接口
    path('auth/login/', login_view, name='login'),
    path('auth/user-info/', user_info_view, name='user-info'),
    path('auth/user/', user_info_view, name='user'),
    path('auth/refresh-token/', refresh_token_view, name='refresh-token'),
]