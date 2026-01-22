from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OfficialColumnViewSet, ColumnArticleViewSet,
    ColumnCommentViewSet, ArticleLikeViewSet,
    column_detail_view, article_detail_view, articles_view
)

# API Routes (using Django REST Framework)
router = DefaultRouter()
router.register(r'columns', OfficialColumnViewSet, basename='column')
router.register(r'articles', ColumnArticleViewSet, basename='article')
router.register(r'comments', ColumnCommentViewSet, basename='comment')
router.register(r'likes', ArticleLikeViewSet, basename='like')

# Web Routes (for rendering templates)
web_urlpatterns = [
    path('', articles_view, name='articles'),
    path('official/<slug:column_slug>/', column_detail_view, name='column_detail'),
    path('official/article/<int:article_id>/', article_detail_view, name='article_detail'),
]


# Combine all routes
# This file is included in main urls.py under both /api/articles/ and /articles/
# So we need to handle both cases
urlpatterns = []

# Add API routes - these will be accessible at /api/articles/...
urlpatterns.extend([
    path('columns/', OfficialColumnViewSet.as_view({'get': 'list'}), name='api_columns'),
    path('columns/<int:pk>/subscribe/', OfficialColumnViewSet.as_view({'post': 'subscribe'}), name='api_columns_subscribe'),
    path('articles/', ColumnArticleViewSet.as_view({'get': 'list'}), name='api_articles'),
    path('articles/infinite_load/', ColumnArticleViewSet.as_view({'get': 'infinite_load'}), name='api_articles_infinite_load'),
    path('comments/', ColumnCommentViewSet.as_view({'get': 'list', 'post': 'create'}), name='api_comments'),
    path('comments/infinite_load/', ColumnCommentViewSet.as_view({'get': 'infinite_load'}), name='api_comments_infinite_load'),
    path('likes/toggle_like/', ArticleLikeViewSet.as_view({'post': 'toggle_like'}), name='api_likes_toggle'),
])

# Add web routes - these will be accessible at /articles/...
urlpatterns.extend(web_urlpatterns)