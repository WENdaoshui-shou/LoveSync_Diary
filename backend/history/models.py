from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class History(models.Model):
    """用户浏览历史模型"""
    HISTORY_TYPES = [
        ('moment', '动态'),
        ('user', '用户主页'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='histories', verbose_name='用户')
    history_type = models.CharField(max_length=20, choices=HISTORY_TYPES, verbose_name='历史类型')
    target_id = models.IntegerField(verbose_name='目标ID')  # 动态ID或用户ID
    viewed_at = models.DateTimeField(auto_now_add=True, verbose_name='浏览时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '浏览历史'
        verbose_name_plural = '浏览历史管理'
        ordering = ['-viewed_at']
        unique_together = ('user', 'history_type', 'target_id')  # 确保每个用户对每个目标只有一条历史记录
    
    def __str__(self):
        return f'{self.user.username} 浏览了 {self.get_history_type_display()} {self.target_id}'
