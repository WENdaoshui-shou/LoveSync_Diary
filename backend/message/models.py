from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Index

User = get_user_model()

# 消息类型枚举
MESSAGE_TYPES = (
    ('system', '系统通知'),
    ('private', '用户私信'),
    ('business', '业务提醒'),
)

class Message(models.Model):
    """消息基础模型"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='接收用户'
    )
    type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPES,
        default='system',
        verbose_name='消息类型'
    )
    content = models.TextField(verbose_name='消息内容')
    is_read = models.BooleanField(
        default=False,
        verbose_name='是否已读'
    )
    is_deleted = models.BooleanField(
        default=False,
        verbose_name='是否已删除'
    )
    create_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    related_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='关联业务ID'
    )
    related_url = models.URLField(
        null=True,
        blank=True,
        verbose_name='关联跳转链接'
    )
    
    class Meta:
        verbose_name = '消息'
        verbose_name_plural = '消息管理'
        ordering = ['-create_time']
        # 添加索引优化查询性能
        indexes = [
            Index(fields=['user', 'is_read', 'create_time']),
            Index(fields=['user', 'is_deleted', 'create_time']),
            Index(fields=['user', 'type', 'create_time']),
        ]
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.content[:20]}"

class PrivateChat(models.Model):
    """私信扩展模型"""
    message = models.OneToOneField(
        Message,
        on_delete=models.CASCADE,
        related_name='private_chat',
        verbose_name='关联消息'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name='发送者'
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name='接收者'
    )
    reply_to = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='replies',
        verbose_name='回复的消息'
    )
    
    class Meta:
        verbose_name = '私信'
        verbose_name_plural = '私信管理'
        ordering = ['-message__create_time']
        indexes = [
            Index(fields=['sender', 'recipient']),
            Index(fields=['recipient', 'sender']),
            Index(fields=['sender']),
            Index(fields=['recipient']),
        ]
    
    def __str__(self):
        return f"{self.sender.username} → {self.recipient.username}: {self.message.content[:20]}"
