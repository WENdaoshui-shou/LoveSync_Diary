from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PhotoViewSet, photo_album, delete_photo, download_photo, photo_album_api

app_name = 'photo'

# API路由
api_router = DefaultRouter()
api_router.register(r'photos', PhotoViewSet, basename='photo')

# Web视图路由
web_urlpatterns = [
    path('album/', photo_album, name='photo_album'),
    path('album/api/', photo_album_api, name='photo_album_api'),
    path('delete/<int:photo_id>/', delete_photo, name='delete_photo'),
    path('download/<int:photo_id>/', download_photo, name='download_photo'),
]

urlpatterns = [
    # API路由
    path('api/', include(api_router.urls)),
    # Web视图路由
    path('', include((web_urlpatterns, 'photo'))),
]