from django.urls import path
from . import views

urlpatterns = [
    # 官方专栏管理 API
    path('columns/', views.get_columns, name='get_columns'),
    path('columns/<int:column_id>/', views.get_column_detail, name='get_column_detail'),
    path('columns/create/', views.create_column, name='create_column'),
    path('columns/<int:column_id>/update/', views.update_column, name='update_column'),
    path('columns/<int:column_id>/delete/', views.delete_column, name='delete_column'),
    
    # 专栏文章管理 API
    path('articles/', views.get_articles, name='get_articles'),
    path('articles/<int:article_id>/', views.get_article_detail, name='get_article_detail'),
    path('articles/create/', views.create_article, name='create_article'),
    path('articles/<int:article_id>/update/', views.update_article, name='update_article'),
    path('articles/<int:article_id>/delete/', views.delete_article, name='delete_article'),
    
    # 专栏评论管理 API
    path('comments/', views.get_comments, name='get_comments'),
    path('comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    
    # 专栏订阅管理 API
    path('subscriptions/', views.get_subscriptions, name='get_subscriptions'),
    
    # 文章点赞管理 API
    path('likes/', views.get_likes, name='get_likes'),
    
    # 统计数据 API
    path('statistics/', views.get_statistics, name='get_statistics'),
]
