from rest_framework import serializers
from .models import OfficialColumn, ColumnArticle, ColumnComment, ColumnSubscription

class OfficialColumnSerializer(serializers.ModelSerializer):
    """官方专栏序列化器"""
    is_subscribed = serializers.SerializerMethodField()
    
    class Meta:
        model = OfficialColumn
        fields = [
            'id', 'name', 'slug', 'description', 'cover_image', 'category',
            'subscriber_count', 'view_count', 'is_active', 'created_at', 'is_subscribed'
        ]
    
    def get_is_subscribed(self, obj):
        """获取当前用户是否订阅"""
        user = self.context.get('user')
        if not user:
            return False
        try:
            subscription = ColumnSubscription.objects.get(user=user, column=obj)
            return subscription.is_subscribed
        except ColumnSubscription.DoesNotExist:
            return False

class ColumnArticleSerializer(serializers.ModelSerializer):
    """专栏文章序列化器"""
    column_name = serializers.CharField(source='column.name')
    column_category = serializers.CharField(source='column.category')
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = ColumnArticle
        fields = [
            'id', 'column', 'column_name', 'column_category', 'title',
            'content', 'cover_image', 'view_count', 'like_count', 'comment_count',
            'published_at', 'is_liked'
        ]
    
    def get_is_liked(self, obj):
        """获取当前用户是否点赞"""
        user = self.context.get('user')
        if not user:
            return False
        from .models import ArticleLike
        return ArticleLike.objects.filter(
            article=obj,
            user=user
        ).exists()

class ColumnCommentSerializer(serializers.ModelSerializer):
    """专栏评论序列化器"""
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_avatar = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = ColumnComment
        fields = [
            'id', 'article', 'user', 'user_name', 'user_avatar', 'content',
            'like_count', 'created_at', 'is_liked'
        ]
        read_only_fields = ['user', 'user_name', 'user_avatar', 'like_count', 'created_at', 'is_liked']

    
    def get_user_avatar(self, obj):
        """获取用户头像"""
        if obj.user.profile and obj.user.profile.userAvatar:
            return obj.user.profile.userAvatar.url
        return ''
    
    def get_is_liked(self, obj):
        """获取当前用户是否点赞"""
        # 暂时返回False，因为我们现在只关注文章点赞功能
        return False

class ColumnSubscriptionSerializer(serializers.ModelSerializer):
    """专栏订阅序列化器"""
    column_name = serializers.CharField(source='column.name')
    column_category = serializers.CharField(source='column.category')
    
    class Meta:
        model = ColumnSubscription
        fields = [
            'id', 'user', 'column', 'column_name', 'column_category',
            'is_subscribed', 'created_at'
        ]