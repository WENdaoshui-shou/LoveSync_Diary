from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NoteViewSet, lovesync

app_name = 'note'

# API路由
api_router = DefaultRouter()
api_router.register(r'notes', NoteViewSet, basename='note')

# Web视图路由
web_urlpatterns = [
    path('lovesync/', lovesync, name='lovesync'),
]

urlpatterns = [
    # API路由 - 不需要额外前缀，因为主URL配置中已经有api/note/前缀
    path('', include(api_router.urls)),
    # Web视图路由 - 使用额外前缀以避免冲突
    path('web/', include((web_urlpatterns, 'note'))),
]