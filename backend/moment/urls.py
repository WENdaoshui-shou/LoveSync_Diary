from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MomentViewSet, TagViewSet, LikeViewSet, FavoriteViewSet, community_view, moments_view, hot_moments_view, share_moment, delete_moment, unshare_moment, moment_share_view

app_name = 'moment'

# API路由
api_router = DefaultRouter()
api_router.register(r'moments', MomentViewSet, basename='moment')
api_router.register(r'tags', TagViewSet, basename='tag')
api_router.register(r'likes', LikeViewSet, basename='like')
api_router.register(r'favorites', FavoriteViewSet, basename='favorite')

# Web视图路由
web_urlpatterns = [
    path('community/', community_view, name='community'),
    path('moments/', moments_view, name='moments'),
    path('hot-moments/', hot_moments_view, name='hot_moments'),

    # 分享动态
    path('share-moment/<int:moment_id>/', share_moment, name='share_moment'),
    # 删除动态
    path('moments/<int:moment_id>/delete/', delete_moment, name='delete_moment'),
    # 取消分享动态
    path('unshare-moment/<int:moment_id>/', unshare_moment, name='unshare_moment'),
    # 动态分享页面（用于外部访问）
    path('community/moment/<int:moment_id>/', moment_share_view, name='moment_share'),
]

urlpatterns = [
    # API路由 - 不需要额外前缀，因为主URL配置中已经有api/moment/前缀
    path('', include(api_router.urls)),
    # Web视图路由 - 使用额外前缀以避免冲突
    path('web/', include((web_urlpatterns, 'moment'))),
]