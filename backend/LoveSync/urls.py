from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from core.views import (
    IndexView, login_view, register_view, logout_view,
    settings_view, verify_code,
    share_place_view
)
from moment.views import community_view, moments_view, hot_moments_view, share_moment, delete_moment, unshare_moment
from photo.views import photo_album, delete_photo, download_photo
from note.views import lovesync

from mall.views import (
    mall, product_detail, add_to_cart, cart_count, 
    mallcart, update_cart, mallmark, checkout
)

urlpatterns = [
    # 核心路由
    path('', IndexView.as_view(), name='index'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('verify_code/', verify_code, name='verify_code'),
    path('settings/<str:setting_type>/', settings_view, name='settings'),
    path('settings/', settings_view, name='settings'),
    path('message/', include('message.urls')),
    
    # 分享功能路由
    path('share/place/<int:place_id>/', share_place_view, name='share_place'),
    
    # 直接映射常用视图，保持向后兼容性
    # Moment应用视图
    path('community/', community_view, name='community'),
    path('moments/', moments_view, name='moments'),
    path('hot-moments/', hot_moments_view, name='hot_moments'),

    # 动态分享、删除和取消分享
    path('share-moment/<int:moment_id>/', share_moment, name='share_moment'),
    path('moments/<int:moment_id>/delete/', delete_moment, name='delete_moment'),
    path('unshare-moment/<int:moment_id>/', unshare_moment, name='unshare_moment'),
    
    # Photo应用视图
    path('photo_album/', photo_album, name='photo_album'),
    path('photo/delete/<int:photo_id>/', delete_photo, name='delete_photo'),
    path('photo/download/<int:photo_id>/', download_photo, name='download_photo'),
    
    # Note应用视图
    path('lovesync/', lovesync, name='lovesync'),
    
    # Mall应用视图
    path('mall/', mall, name='mall'),
    path('product_detail/<int:product_id>/', product_detail, name='product_detail'),
    path('add-to-cart/', add_to_cart, name='add_to_cart'),
    path('cart-count/', cart_count, name='cart_count'),
    path('mallcart/', mallcart, name='mallcart'),
    path('update-cart/', update_cart, name='update_cart'),
    path('mallmark/', mallmark, name='mallmark'),
    path('checkout/', checkout, name='checkout'),
    path('checkout/<int:product_id>/', checkout, name='checkout_with_id'),
    
    # AI应用路由
    path('AI/', include('AI.urls')),
    
    # 管理后台
    path('admin/', admin.site.urls),
    
    # 静态文件
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# API路由 - 单独定义，使用不同的命名空间
api_urlpatterns = [
    path('api/core/', include('core.urls', namespace='core_api')),
    path('api/moment/', include('moment.urls', namespace='moment_api')),
    path('api/couple/', include('couple.urls', namespace='couple_api')),
    path('api/mall/', include('mall.urls', namespace='mall_api')),
    path('api/photo/', include('photo.urls', namespace='photo_api')),
    path('api/note/', include('note.urls', namespace='note_api')),
    path('api/game/', include('game.urls', namespace='game_api')),
    path('api/articles/', include('articles.urls')),
    path('api/community/', include('sys_community.urls', namespace='sys_community_api')),
]

# Web视图路由 - 单独定义，使用不同的命名空间
web_urlpatterns = [
    path('core/', include('core.urls')),
    path('moment/', include('moment.urls', namespace='moment_web')),
    path('couple/', include('couple.urls', namespace='couple_web')),
    path('mall/', include('mall.urls', namespace='mall_web')),
    path('photo/', include('photo.urls', namespace='photo_web')),
    path('note/', include('note.urls', namespace='note_web')),
    path('game/', include('game.urls', namespace='game_web')),
    path('vip/', include('vip.urls', namespace='vip_web')),
    path('user/', include('user.urls', namespace='user')),
    path('articles/', include('articles.urls')),
    path('history/', include('history.urls', namespace='history')),  # 添加历史应用路由
    path('collab/', include('collab.urls', namespace='collab')),  # 添加协作功能路由
]

# 将API路由和Web视图路由添加到主URL列表中
urlpatterns += api_urlpatterns + web_urlpatterns
