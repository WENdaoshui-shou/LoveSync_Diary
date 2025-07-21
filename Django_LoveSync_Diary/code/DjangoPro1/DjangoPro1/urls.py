from django.contrib import admin
from django.urls import path
from App.views import *
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 首页
    path('', user_index, name='index'),
    path('index/', user_index, name='index'),

    # 登录
    path('login/', user_login, name='login'),
    # 添加验证码路由
    path('verify_code/', verify_code, name='verify_code'),

    # 退出登录
    path('logout/', user_logout, name='logout'),

    # 注册
    path('register/', user_register, name='register'),

    # 社区
    path('community/', community, name='community'),

    # 消息
    path('message/', message, name='message'),

    # # 设置
    # path('settings/', settings_view, name='settings'),
    # 个人设置页面 - 带tab参数
    path('settings/<str:tab>/', settings_view, name='settings'),
    # 个人设置页面 - 默认显示profile选项卡
    path('settings/', settings_view, {'tab': 'profile'}, name='settings'),

    # 主页
    path('personal_center/', personal_center, name='personal_center'),

    # 相册
    path('photo_album/', photo_album, name='photo_album'),
    # 删除照片
    path('photo/<int:photo_id>/', delete_photo, name='delete_photo'),

    # 收藏
    path('favorites/', favorites, name='favorites'),

    # 双人日记
    path('lovesync/', lovesync, name='lovesync'),

    # 动态
    path('moments/', moments, name='moments'),
    # 分享动态
    path('share-moment/<int:moment_id>/', share_moment, name='share_moment'),
    # 取消分享动态
    path('unshare-moment/<int:moment_id>/', unshare_moment, name='unshare_moment'),
    # 删除动态
    path('moments/<int:moment_id>/delete/', delete_moment, name='delete_moment'),

    # 购物商城
    path('mall/', mall, name='mall'),
    # 购物车
    path('mallcart/', mallcart, name='mallcart'),
    # 添加到购物车
    path('add_to_cart/', add_to_cart, name='add_to_cart'),
    # 收藏
    path('mallmark/', mallmark, name='mallmark'),
    # 商品详情
    path('product/<uuid:product_id>/', product_detail, name='product_detail'),
    # 结算
    path('checkout/<uuid:product_id>/', checkout, name='checkout'),

    path('admin/', admin.site.urls),
]

# 添加媒体文件路由（仅在开发环境使用）
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
