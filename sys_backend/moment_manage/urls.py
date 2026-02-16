from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MomentViewSet, CommentViewSet

app_name = 'moment_manage'

# API路由
router = DefaultRouter()
router.register(r'moments', MomentViewSet, basename='moment')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
]