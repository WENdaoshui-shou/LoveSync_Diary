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


# 测试题目分类表
class QuizCategory(models.Model):
    """测试题目分类"""
    name = models.CharField(max_length=50, verbose_name='分类名称', unique=True)
    description = models.TextField(verbose_name='分类描述', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '测试题目分类'
        verbose_name_plural = '测试题目分类管理'
        ordering = ['name']
    
    def __str__(self):
        return self.name

# 测试问题表
class QuizQuestion(models.Model):
    """测试问题表"""
    category = models.ForeignKey(QuizCategory, on_delete=models.CASCADE, related_name='questions', verbose_name='所属分类')
    question = models.TextField(verbose_name='问题')
    options = models.JSONField(verbose_name='选项列表')  # 使用JSONField存储选项
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '测试问题'
        verbose_name_plural = '测试问题管理'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.question

# 用户测试答案记录表
class UserQuizAnswer(models.Model):
    """用户测试答案记录"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_answers', verbose_name='用户')
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='user_answers', verbose_name='问题')
    selected_option = models.CharField(max_length=100, verbose_name='选择的选项')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='答题时间')
    
    class Meta:
        verbose_name = '用户测试答案'
        verbose_name_plural = '用户测试答案管理'
        unique_together = ('user', 'question')  # 确保用户对每个问题只回答一次
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.question.question[:30]}'


class CouplePlace(models.Model):
    """情侣地点模型"""
    PLACE_TYPE_CHOICES = [
        ('romantic', '浪漫约会'),
        ('outdoor', '户外探险'),
        ('cultural', '文化体验'),
        ('dining', '美食餐厅'),
        ('entertainment', '休闲娱乐'),
        ('free', '免费景点'),
        ('other', '其他'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='地点名称')
    description = models.TextField(verbose_name='地点描述')
    address = models.CharField(max_length=200, verbose_name='地址')
    latitude = models.FloatField(verbose_name='纬度')
    longitude = models.FloatField(verbose_name='经度')
    place_type = models.CharField(max_length=20, choices=PLACE_TYPE_CHOICES, verbose_name='地点类型')
    rating = models.FloatField(default=0, verbose_name='评分')
    review_count = models.IntegerField(default=0, verbose_name='评价数量')
    price_range = models.CharField(max_length=50, verbose_name='价格范围')
    image_url = models.URLField(blank=True, null=True, verbose_name='图片URL')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '情侣地点'
        verbose_name_plural = '情侣地点管理'
        ordering = ['-rating', '-review_count']
    
    def __str__(self):
        return self.name


class MusicPlayer(models.Model):
    """音乐播放器模型"""
    title = models.CharField(max_length=100, verbose_name='歌曲标题')
    artist = models.CharField(max_length=100, verbose_name='歌手')
    album_cover = models.ImageField(
        upload_to='music_covers/',
        blank=True,
        null=True,
        verbose_name='专辑封面'
    )
    audio_file = models.FileField(
        upload_to='music_files/',
        blank=True,
        null=True,
        verbose_name='音频文件'
    )
    is_currently_playing = models.BooleanField(default=False, verbose_name='是否正在播放')
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='music_player')
    
    def __str__(self):
        return f"{self.title} - {self.artist}"


class LoveStoryTimeline(models.Model):
    """爱情故事时间线模型"""
    title = models.CharField(max_length=100, verbose_name='事件标题')
    description = models.TextField(verbose_name='事件描述')
    date = models.DateField(verbose_name='事件日期')
    image = models.ImageField(
        upload_to='love_story_images/',
        blank=True,
        null=True,
        verbose_name='事件图片'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='love_story_timeline')
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.title} - {self.date}"


class CoupleRelationHistory(models.Model):
    """情侣关系历史模型"""
    started_at = models.DateTimeField(verbose_name='开始时间')
    ended_at = models.DateTimeField(verbose_name='结束时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='记录创建时间')
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='relation_history_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='relation_history_as_user2')
    
    class Meta:
        verbose_name = '情侣关系历史'
        verbose_name_plural = '情侣关系历史记录'
        ordering = ['-ended_at']
    
    def __str__(self):
        return f"Relationship from {self.started_at.date()} to {self.ended_at.date()}"


class CoupleQuiz(models.Model):
    """情侣测试模型"""
    question = models.TextField(verbose_name='问题')
    correct_answer = models.CharField(max_length=100, verbose_name='正确答案')
    options = models.JSONField(verbose_name='选项列表')
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='couple_quizzes')
    
    def __str__(self):
        return self.question[:50]
