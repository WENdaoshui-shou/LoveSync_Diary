from django.contrib import admin
from .models import (
    OfficialColumn, ColumnArticle, ColumnComment,
    ArticleLike, ColumnSubscription
)

@admin.register(OfficialColumn)
class OfficialColumnAdmin(admin.ModelAdmin):
    """官方专栏后台管理"""
    list_display = ['name', 'category', 'subscriber_count', 'view_count', 'is_active', 'updated_at']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['-updated_at']


@admin.register(ColumnArticle)
class ColumnArticleAdmin(admin.ModelAdmin):
    """专栏文章后台管理"""
    list_display = ['title', 'column', 'view_count', 'like_count', 'comment_count', 'published_at']
    list_filter = ['column', 'published_at']
    search_fields = ['title', 'content']
    ordering = ['-published_at']


@admin.register(ColumnComment)
class ColumnCommentAdmin(admin.ModelAdmin):
    """专栏评论后台管理"""
    list_display = ['article', 'user', 'content', 'like_count', 'created_at']
    list_filter = ['article', 'created_at']
    search_fields = ['content', 'user__username']
    ordering = ['-created_at']


@admin.register(ArticleLike)
class ArticleLikeAdmin(admin.ModelAdmin):
    """文章点赞后台管理"""
    list_display = ['article', 'user', 'created_at']
    list_filter = ['article', 'created_at']
    search_fields = ['user__username']
    ordering = ['-created_at']


@admin.register(ColumnSubscription)
class ColumnSubscriptionAdmin(admin.ModelAdmin):
    """专栏订阅后台管理"""
    list_display = ['user', 'column', 'is_subscribed', 'created_at']
    list_filter = ['column', 'is_subscribed']
    search_fields = ['user__username', 'column__name']
    ordering = ['-created_at']
