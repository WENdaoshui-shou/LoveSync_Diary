from django.db import models
import uuid
from django.utils import timezone


class ChatSession(models.Model):
    """存储聊天会话信息"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    completed = models.BooleanField(default=False)
    user_final_selection = models.JSONField(null=True, blank=True)  # 存储用户最终选择的参数

    class Meta:
        ordering = ['-updated_at']
        verbose_name = '聊天会话'
        verbose_name_plural = '聊天会话'

    def __str__(self):
        return f"会话 {self.id} {'已完成' if self.completed else '进行中'}"


class ChatMessage(models.Model):
    """存储聊天消息记录"""
    ROLE_CHOICES = (
        ('system', '系统'),
        ('user', '用户'),
        ('assistant', '助手'),
    )

    id = models.AutoField(primary_key=True)
    session = models.ForeignKey(ChatSession, related_name='messages', on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at']
        verbose_name = '聊天消息'
        verbose_name_plural = '聊天消息'

    def __str__(self):
        return f"{self.get_role_display()}消息: {self.content[:30]}..."


class PhoneRecommendation(models.Model):
    """存储手机推荐结果"""
    id = models.AutoField(primary_key=True)
    session = models.OneToOneField(ChatSession, on_delete=models.CASCADE, related_name='recommendation')
    screen_size = models.CharField(max_length=10)  # 6.1英寸、6.5英寸、6.7英寸
    resolution = models.CharField(max_length=5)  # 2K、4K
    recommended_phones = models.JSONField()  # 存储推荐的手机列表
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = '手机推荐'
        verbose_name_plural = '手机推荐'

    def __str__(self):
        return f"{self.screen_size} {self.resolution} 推荐"
