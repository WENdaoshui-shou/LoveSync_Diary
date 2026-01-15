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