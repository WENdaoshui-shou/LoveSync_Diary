from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Index

User = get_user_model()

class Follow(models.Model):
    """关注关系模型"""
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_following',
        verbose_name='关注者'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_followers',
        verbose_name='被关注者'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='关注时间'
    )
    is_deleted = models.BooleanField(
        default=False,
        verbose_name='是否已取消关注'
    )
    
    class Meta:
        verbose_name = '关注关系'
        verbose_name_plural = '关注关系管理'
        unique_together = ('follower', 'following')
        indexes = [
            Index(fields=['follower', 'following', 'is_deleted']),
            Index(fields=['following', 'is_deleted']),
            Index(fields=['follower', 'is_deleted']),
        ]
    
    def __str__(self):
        return f"{self.follower.name} 关注了 {self.following.name}"


class Collection(models.Model):
    """用户收藏模型"""
    # 收藏类型选择
    CONTENT_TYPE_CHOICES = [
        ('moment', '动态'),
        ('place', '地点'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='collections',
        verbose_name='用户'
    )
    content_type = models.CharField(
        max_length=10,
        choices=CONTENT_TYPE_CHOICES,
        verbose_name='收藏类型'
    )
    object_id = models.PositiveIntegerField(
        verbose_name='收藏对象ID'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='收藏时间'
    )
    
    class Meta:
        verbose_name = '用户收藏'
        verbose_name_plural = '用户收藏管理'
        # 联合唯一索引，避免重复收藏
        unique_together = ('user', 'content_type', 'object_id')
        indexes = [
            # 用户+类型+对象ID的唯一索引
            Index(fields=['user', 'content_type', 'object_id'], name='unique_user_content_object'),
            # 用户+类型的索引，用于快速查询用户收藏的特定类型内容
            Index(fields=['user', 'content_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.name} 收藏了 {self.content_type} {self.object_id}"