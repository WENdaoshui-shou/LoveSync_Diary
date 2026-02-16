from rest_framework import serializers
from .models import Moment, MomentImage, Comment, Tag
from django.contrib.auth import get_user_model

User = get_user_model()


class MomentListSerializer(serializers.ModelSerializer):
    """动态列表序列化器"""
    user = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    
    def get_user(self, obj):
        """获取用户信息"""
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'name': obj.user.first_name or obj.user.username,
            'email': obj.user.email
        }
    
    def get_images(self, obj):
        """获取动态图片"""
        images = obj.moment_images.all()
        return [image.image.url for image in images] if images else []
    
    def get_tags(self, obj):
        """获取标签"""
        tags = obj.tags.all()
        return [tag.name for tag in tags] if tags else []
    
    def get_created_at(self, obj):
        """格式化创建时间"""
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
    
    def get_status_display(self, obj):
        """获取状态显示文本"""
        return '已分享' if obj.is_shared else '未分享'
    
    class Meta:
        model = Moment
        fields = ['id', 'user', 'content', 'likes', 'comments', 'favorites', 'view_count', 
                 'created_at', 'is_shared', 'status_display', 'images', 'tags']


class MomentDetailSerializer(serializers.ModelSerializer):
    """动态详情序列化器"""
    user = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    hot_score = serializers.SerializerMethodField()
    
    def get_user(self, obj):
        """获取用户信息"""
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'name': obj.user.first_name or obj.user.username,
            'email': obj.user.email,
            'is_active': obj.user.is_active,
            'date_joined': obj.user.date_joined.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_images(self, obj):
        """获取动态图片"""
        images = obj.moment_images.all()
        return [{
            'id': image.id,
            'url': image.image.url
        } for image in images] if images else []
    
    def get_tags(self, obj):
        """获取标签详情"""
        tags = obj.tags.all()
        return [{
            'id': tag.id,
            'name': tag.name,
            'created_at': tag.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for tag in tags] if tags else []
    
    def get_created_at(self, obj):
        """格式化创建时间"""
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
    
    def get_status_display(self, obj):
        """获取状态显示文本"""
        return '已分享' if obj.is_shared else '未分享'
    
    def get_hot_score(self, obj):
        """计算热度值"""
        return obj.get_hot_score()
    
    class Meta:
        model = Moment
        fields = ['id', 'user', 'content', 'likes', 'comments', 'favorites', 'view_count',
                 'created_at', 'is_shared', 'status_display', 'images', 'tags', 'hot_score']


class CommentSerializer(serializers.ModelSerializer):
    """评论序列化器"""
    user = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    parent_comment = serializers.SerializerMethodField()
    
    def get_user(self, obj):
        """获取评论用户信息"""
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'name': obj.user.first_name or obj.user.username,
            'email': obj.user.email
        }
    
    def get_created_at(self, obj):
        """格式化创建时间"""
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
    
    def get_parent_comment(self, obj):
        """获取父评论信息"""
        if obj.parent:
            return {
                'id': obj.parent.id,
                'user': obj.parent.user.username,
                'content': obj.parent.content[:50]
            }
        return None
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'likes', 'created_at', 'parent', 'parent_comment']


class TagSerializer(serializers.ModelSerializer):
    """标签序列化器"""
    moment_count = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    
    def get_moment_count(self, obj):
        """获取标签关联的动态数量"""
        return obj.moments.count()
    
    def get_created_at(self, obj):
        """格式化创建时间"""
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'moment_count', 'created_at']