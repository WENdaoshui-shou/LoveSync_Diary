from django.db import models


class CommunityEvent(models.Model):
    STATUS_CHOICES = [
        ('active', '进行中'),
        ('upcoming', '即将开始'),
        ('ended', '已结束'),
    ]

    title = models.CharField(max_length=200, verbose_name='活动标题')
    description = models.TextField(verbose_name='活动描述')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming', verbose_name='活动状态')
    image = models.ImageField(upload_to='sys_images/community/community_active_images/', blank=True, null=True, verbose_name='活动图片')
    start_date = models.DateTimeField(blank=True, null=True, verbose_name='开始时间')
    end_date = models.DateTimeField(blank=True, null=True, verbose_name='结束时间')
    location = models.CharField(max_length=200, blank=True, null=True, verbose_name='活动地点')
    participant_count = models.IntegerField(default=0, verbose_name='参与人数')
    prize_info = models.TextField(blank=True, null=True, verbose_name='奖品信息')
    is_pinned = models.BooleanField(default=False, verbose_name='是否置顶')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'sys_community_active'
        ordering = ['-is_pinned', '-created_at']
        verbose_name = '社区活动'
        verbose_name_plural = '社区活动'

    def __str__(self):
        return self.title

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, '未知')
