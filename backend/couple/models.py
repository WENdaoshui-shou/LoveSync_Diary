from django.db import models
from core.models import User
from django.utils import timezone


class Anniversary(models.Model):
    """纪念日模型"""
    TYPE_CHOICES = [
        ('love_start', '相恋日'),
        ('first_date', '第一次约会'),
        ('valentine', '情人节'),
        ('birthday_partner', '伴侣生日'),
        ('anniversary', '结婚纪念日'),
        ('custom', '自定义'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='anniversaries')
    title = models.CharField(max_length=100, verbose_name='纪念日标题')
    anniversary_date = models.DateField(verbose_name='纪念日日期')
    anniversary_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='custom', verbose_name='纪念日类型')
    description = models.TextField(null=True, blank=True, verbose_name='纪念日描述')
    is_reminder_enabled = models.BooleanField(default=True, verbose_name='启用提醒')
    reminder_days = models.IntegerField(default=1, verbose_name='提前提醒天数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '纪念日'
        verbose_name_plural = '纪念日管理'
        ordering = ['anniversary_date']
    
    def __str__(self):
        return f"{self.title} - {self.anniversary_date}"
    
    def get_days_until(self):
        """计算距离纪念日还有多少天"""
        today = timezone.now().date()
        next_anniversary = self.anniversary_date.replace(year=today.year)
        
        # 如果今年的纪念日已经过了，计算到明年的
        if next_anniversary < today:
            next_anniversary = next_anniversary.replace(year=today.year + 1)
        
        return (next_anniversary - today).days
    
    def is_upcoming(self):
        """检查纪念日是否即将到来（提前提醒天数内）"""
        return self.get_days_until() <= self.reminder_days
    
    def get_anniversary_years(self):
        """计算已经过了多少年"""
        today = timezone.now().date()
        return today.year - self.anniversary_date.year


class CoupleTask(models.Model):
    """情侣任务模型"""
    STATUS_CHOICES = [
        ('pending', '待完成'),
        ('completed', '已完成'),
        ('failed', '已失败'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=100, verbose_name='任务标题')
    description = models.TextField(null=True, blank=True, verbose_name='任务描述')
    deadline = models.DateTimeField(verbose_name='截止时间')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='任务状态')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    is_shared = models.BooleanField(default=True, verbose_name='是否共享给伴侣')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '情侣任务'
        verbose_name_plural = '情侣任务管理'
        ordering = ['deadline']
    
    def __str__(self):
        return f"{self.title} - {self.status}"
    
    def is_overdue(self):
        """检查任务是否逾期"""
        return self.status == 'pending' and self.deadline < timezone.now()
    
    def complete_task(self):
        """完成任务"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
        return True
    
    def fail_task(self):
        """标记任务失败"""
        self.status = 'failed'
        self.save()
        return True


class TaskCompletion(models.Model):
    """任务完成记录，用于记录情侣双方的任务完成情况"""
    task = models.ForeignKey(CoupleTask, on_delete=models.CASCADE, related_name='completions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_completions')
    is_completed = models.BooleanField(default=False, verbose_name='是否完成')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        unique_together = ('task', 'user')
        verbose_name = '任务完成记录'
        verbose_name_plural = '任务完成记录'
    
    def __str__(self):
        return f"{self.user.username} - {self.task.title} - {'已完成' if self.is_completed else '未完成'}"
    
    def complete(self):
        """完成任务"""
        self.is_completed = True
        self.completed_at = timezone.now()
        self.save()
        return True
