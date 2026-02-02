from rest_framework import serializers
from .models import Moment, MomentImage, Comment, Tag, Like
from core.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    """标签序列化器"""
    moment_count = serializers.SerializerMethodField()
    
    def get_moment_count(self, obj):
        """获取标签关联的动态数量"""
        return obj.moments.count()
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'created_at', 'moment_count']


class MomentImageSerializer(serializers.ModelSerializer):
    """动态图片序列化器"""
    class Meta:
        model = MomentImage
        fields = ['id', 'image']


class CommentSerializer(serializers.ModelSerializer):
    """评论序列化器"""
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    
    def get_replies(self, obj):
        """获取评论的回复"""
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at', 'parent', 'replies']


class MomentSerializer(serializers.ModelSerializer):
    """动态序列化器"""
    user = UserSerializer(read_only=True)
    moment_images = MomentImageSerializer(many=True, read_only=True)
    comment_set = CommentSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = Moment
        fields = ['id', 'user', 'content', 'likes', 'comments', 'favorites', 'created_at', 'is_shared', 'moment_images', 'comment_set', 'tags', 'view_count']
    
    def create(self, validated_data):
        """创建动态"""
        images_data = self.context['request'].FILES.getlist('images')
        tags_data = self.context['request'].data.getlist('tags', [])
        
        moment = Moment.objects.create(**validated_data)
        
        # 处理图片
        for image_data in images_data:
            MomentImage.objects.create(moment=moment, image=image_data)
        
        # 处理标签
        for tag_name in tags_data:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            moment.tags.add(tag)
        
        return moment


class LikeSerializer(serializers.ModelSerializer):
    """点赞序列化器"""
    user = UserSerializer(read_only=True)
    moment = MomentSerializer(read_only=True)
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'moment', 'created_at']
    
    def create(self, validated_data):
        """创建点赞记录"""
        return Like.objects.create(**validated_data)



