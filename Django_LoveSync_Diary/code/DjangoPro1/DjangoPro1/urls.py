from django.contrib import admin
from django.urls import path
from App.views import *
urlpatterns = [
    # 首页
    path('', user_index, name='index'),
    path('index/', user_index, name='index'),

    # 登录
    path('login/', user_login, name='login'),

    # 注册
    path('register/', user_register, name='register'),

    path('admin/', admin.site.urls),
]
