from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomTokenObtainPairView, RegisterViewSet, ProfileViewSet, LoginViewSet,
    settings_view, message_view
)
from core.views import community_view
app_name = 'core'

# API路由
api_router = DefaultRouter()
api_router.register(r'register', RegisterViewSet, basename='register')
api_router.register(r'profile', ProfileViewSet, basename='profile')
api_router.register(r'login', LoginViewSet, basename='login')

# Web视图路由
urlpatterns = [
    # API路由
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token'),
    path('api/', include(api_router.urls)),
    # Web视图路由
    path('settings/<str:setting_type>/', settings_view, name='settings'),
    path('settings/', settings_view, name='settings'),
    path('message/', message_view, name='message'),
    path('community/', community_view, name='community'),
]
