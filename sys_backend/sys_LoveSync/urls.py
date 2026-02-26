"""
URL configuration for sys_LoveSync project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin-api/user/', include('user_manage.urls')),
    path('admin-api/moment/', include('moment_manage.urls')),
    path('admin-api/community/', include('community_manage.urls')),
    path('admin-api/couple/', include('couple_manage.urls')),
    path('admin-api/mall/', include('mall_manage.urls')),
    path('admin-api/articles_manage/', include('articles_manage.urls')),
]

# 添加媒体文件静态路由
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)