from django.contrib import admin
from django.urls import path
from App.views import *
from django.contrib import admin
from django.urls import include, path
from django.conf import settings  # 导入 settings
from django.conf.urls.static import static  # 导入 static

urlpatterns = [
    # 首页
    path('', user_index, name='index'),
    path('index/', user_index, name='index'),

    # 登录
    path('login/', user_login, name='login'),

    # 退出登录
    path('logout/', user_logout, name='logout'),

    # 注册
    path('register/', user_register, name='register'),

    # 社区
    path('community/', community, name='community'),

    # 消息
    path('message/', message, name='message'),

    # 设置
    path('settings/', settings_view, name='settings'),

    # 主页
    path('Personal_Center/', Personal_Center, name='Personal_Center'),

    # 相册
    path('Photo_album/', Photo_album, name='Photo_album'),

    # 收藏
    path('favorites/', favorites, name='favorites'),

    # 动态
    path('moments/', moments, name='moments'),

    path('admin/', admin.site.urls),
]

# 添加媒体文件路由（仅在开发环境使用）
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

