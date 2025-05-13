from django.contrib import admin
from django.urls import path
from App.views import *
urlpatterns = [
    # 首页
    path('/', user_index),
    path('index/', user_index, name='index'),

    path('admin/', admin.site.urls),
]
