from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CommunityEventViewSet,
    ReportViewSet,
    ArticleColumnViewSet,
    TopicViewSet,
)

app_name = 'community_manage'

# API路由
router = DefaultRouter()
router.register(r'events', CommunityEventViewSet, basename='community-event')
router.register(r'reports', ReportViewSet, basename='community-report')
router.register(r'articles', ArticleColumnViewSet, basename='community-article')
router.register(r'topics', TopicViewSet, basename='community-topic')

urlpatterns = [
    path('', include(router.urls)),
]