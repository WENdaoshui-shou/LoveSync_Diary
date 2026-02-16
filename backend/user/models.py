from django.db import models
from django.db.models import Index
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from core.models import User
from django.db import models
from django.utils import timezone

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


# 成就定义模型
class Achievement(models.Model):
    """成就定义模型"""
    title = models.CharField(max_length=100, verbose_name='成就标题')
    description = models.TextField(verbose_name='成就描述')
    icon = models.CharField(max_length=10, verbose_name='成就图标')  # 使用emoji作为图标
    requirement = models.CharField(max_length=200, verbose_name='解锁要求')
    category = models.CharField(max_length=50, verbose_name='成就分类')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '成就'
        verbose_name_plural = '成就管理'
        ordering = ['category', 'title']
    
    def __str__(self):
        return f'{self.title} - {self.category}'

# 用户成就模型
class UserAchievement(models.Model):
    """用户成就模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_achievements', verbose_name='用户')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='user_achievements', verbose_name='成就')
    unlocked = models.BooleanField(default=False, verbose_name='是否解锁')
    progress = models.IntegerField(default=0, verbose_name='进度')
    unlocked_at = models.DateTimeField(null=True, blank=True, verbose_name='解锁时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户成就'
        verbose_name_plural = '用户成就管理'
        unique_together = ('user', 'achievement')
        ordering = ['-unlocked_at', '-updated_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.achievement.title}'

    def unlock(self):
        """解锁成就"""
        if not self.unlocked:
            self.unlocked = True
            self.progress = 100
            self.unlocked_at = timezone.now()
            self.save()
            return True
        return False

    def update_progress(self, new_progress):
        """更新成就进度"""
        old_progress = self.progress
        self.progress = min(new_progress, 100)
        
        # 如果进度达到100%，自动解锁成就
        if self.progress >= 100 and not self.unlocked:
            self.unlock()
        else:
            self.save()
        
        return self.progress != old_progress


# 监听动态创建事件，解锁"记录美好"成就
def unlock_record_moment_achievement(sender, instance, created, **kwargs):
    """当用户创建第一条动态时，解锁"记录美好"成就"""
    if created:
        user = instance.user
        # 检查用户是否是第一次创建动态
        moment_count = sender.objects.filter(user=user).count()
        if moment_count == 1:
            # 查找"记录美好"成就
            try:
                achievement = Achievement.objects.get(title='记录美好')
                # 获取用户成就记录
                user_achievement, created = UserAchievement.objects.get_or_create(
                    user=user,
                    achievement=achievement
                )
                # 解锁成就
                user_achievement.unlock()
            except Achievement.DoesNotExist:
                pass

# 监听照片上传事件，解锁"爱的相册"成就
def unlock_photo_album_achievement(sender, instance, created, **kwargs):
    """当用户上传第一张照片时，解锁"爱的相册"成就"""
    if created:
        user = instance.user
        # 检查用户是否是第一次上传照片
        photo_count = sender.objects.filter(user=user).count()
        if photo_count == 1:
            # 查找"爱的相册"成就
            try:
                achievement = Achievement.objects.get(title='爱的相册')
                # 获取用户成就记录
                user_achievement, created = UserAchievement.objects.get_or_create(
                    user=user,
                    achievement=achievement
                )
                # 解锁成就
                user_achievement.unlock()
            except Achievement.DoesNotExist:
                pass

# 监听情侣绑定事件，解锁"初次相遇"成就
@receiver(post_save, sender=User)
def unlock_first_meeting_achievement(sender, instance, created, **kwargs):
    """当用户绑定情侣关系时，解锁"初次相遇"成就"""
    if not created and hasattr(instance, 'profile') and instance.profile.couple:
        if instance.profile.couple_joined_at:
            try:
                achievement = Achievement.objects.get(title='初次相遇')
                user_achievement, created = UserAchievement.objects.get_or_create(
                    user=instance,
                    achievement=achievement
                )
                user_achievement.unlock()
            except Achievement.DoesNotExist:
                pass

# 监听情侣测试事件，解锁"甜蜜开始"成就
def unlock_sweet_beginning_achievement(sender, instance, created, **kwargs):
    """当用户完成情侣测试时，解锁"甜蜜开始"成就"""
    if created:
        user = instance.user
        # 检查用户是否是第一次完成情侣测试
        quiz_count = sender.objects.filter(user=user).count()
        if quiz_count == 1:
            # 查找"甜蜜开始"成就
            try:
                achievement = Achievement.objects.get(title='甜蜜开始')
                # 获取用户成就记录
                user_achievement, created = UserAchievement.objects.get_or_create(
                    user=user,
                    achievement=achievement
                )
                # 解锁成就
                user_achievement.unlock()
            except Achievement.DoesNotExist:
                pass

# 监听情侣地点事件，解锁"爱的足迹"成就
def unlock_love_journey_achievement(sender, instance, created, **kwargs):
    """当用户添加情侣地点时，解锁"爱的足迹"成就"""
    if created:
        user = instance.user
        # 检查用户是否是第一次添加情侣地点
        place_count = sender.objects.filter(user=user).count()
        if place_count == 1:
            # 查找"爱的足迹"成就
            try:
                achievement = Achievement.objects.get(title='爱的足迹')
                # 获取用户成就记录
                user_achievement, created = UserAchievement.objects.get_or_create(
                    user=user,
                    achievement=achievement
                )
                # 解锁成就
                user_achievement.unlock()
            except Achievement.DoesNotExist:
                pass

# 监听游戏分数事件，解锁"游戏达人"成就
def unlock_game_master_achievement(sender, instance, created, **kwargs):
    """当用户获得游戏分数时，解锁"游戏达人"成就"""
    if created:
        user = instance.user
        # 检查用户是否是第一次获得游戏分数
        score_count = sender.objects.filter(user=user).count()
        if score_count == 1:
            # 查找"游戏达人"成就
            try:
                achievement = Achievement.objects.get(title='游戏达人')
                # 获取用户成就记录
                user_achievement, created = UserAchievement.objects.get_or_create(
                    user=user,
                    achievement=achievement
                )
                # 解锁成就
                user_achievement.unlock()
            except Achievement.DoesNotExist:
                pass

# 监听纪念日事件，解锁"纪念时刻"成就
def unlock_anniversary_moment_achievement(sender, instance, created, **kwargs):
    """当用户添加纪念日时，解锁"纪念时刻"成就"""
    if created:
        user = instance.user
        # 检查用户是否是第一次添加纪念日
        anniversary_count = sender.objects.filter(user=user).count()
        if anniversary_count == 1:
            # 查找"纪念时刻"成就
            try:
                achievement = Achievement.objects.get(title='纪念时刻')
                # 获取用户成就记录
                user_achievement, created = UserAchievement.objects.get_or_create(
                    user=user,
                    achievement=achievement
                )
                # 解锁成就
                user_achievement.unlock()
            except Achievement.DoesNotExist:
                pass

# 监听用户登录事件，解锁"每日打卡"成就
@receiver(user_logged_in)
def unlock_daily_checkin_achievement(sender, request, user, **kwargs):
    """当用户登录时，更新"每日打卡"成就"""
    try:
        achievement = Achievement.objects.get(title='每日打卡')
        # 获取用户成就记录
        user_achievement, created = UserAchievement.objects.get_or_create(
            user=user,
            achievement=achievement
        )
        
        # 简单的打卡逻辑：每次登录增加10%进度，达到100%解锁
        new_progress = min(user_achievement.progress + 10, 100)
        user_achievement.update_progress(new_progress)
        
        if new_progress >= 100:
            user_achievement.unlock()
    except Achievement.DoesNotExist:
        pass

# 监听情侣关系周年事件，解锁"一周年纪念"成就
@receiver(post_save, sender=User)
def unlock_anniversary_achievement(sender, instance, created, **kwargs):
    """当情侣关系满一周年时，解锁"一周年纪念"成就"""
    if not created and hasattr(instance, 'profile') and instance.profile.couple and instance.profile.couple_joined_at:
        # 计算情侣关系持续时间
        joined_at = instance.profile.couple_joined_at
        now = timezone.now()
        years = now.year - joined_at.year
        
        # 检查是否满一周年
        if years >= 1:
            try:
                achievement = Achievement.objects.get(title='一周年纪念')
                # 获取用户成就记录
                user_achievement, created = UserAchievement.objects.get_or_create(
                    user=instance,
                    achievement=achievement
                )
                # 解锁成就
                user_achievement.unlock()
            except Achievement.DoesNotExist:
                pass

# 监听关注事件，解锁"社交达人"成就
@receiver(post_save, sender=Follow)
def unlock_social_master_achievement(sender, instance, created, **kwargs):
    """当用户关注人数达到一定数量时，解锁"社交达人"成就"""
    if created and not instance.is_deleted:
        user = instance.follower
        # 检查用户关注人数
        following_count = Follow.objects.filter(follower=user, is_deleted=False).count()
        
        # 当关注人数达到10人时，解锁"社交达人"成就
        if following_count >= 10:
            try:
                achievement = Achievement.objects.get(title='社交达人')
                # 获取用户成就记录
                user_achievement, created = UserAchievement.objects.get_or_create(
                    user=user,
                    achievement=achievement
                )
                # 解锁成就
                user_achievement.unlock()
            except Achievement.DoesNotExist:
                pass


# 导入并注册信号
try:
    from moment.models import Moment
    post_save.connect(unlock_record_moment_achievement, sender=Moment)
except ImportError:
    pass

try:
    from photo.models import Photo
    post_save.connect(unlock_photo_album_achievement, sender=Photo)
except ImportError:
    pass

try:
    from couple.models import CoupleQuiz
    post_save.connect(unlock_sweet_beginning_achievement, sender=CoupleQuiz)
except ImportError:
    pass

try:
    from couple.models import CouplePlace
    post_save.connect(unlock_love_journey_achievement, sender=CouplePlace)
except ImportError:
    pass

try:
    from game.models import GameScore
    post_save.connect(unlock_game_master_achievement, sender=GameScore)
except ImportError:
    pass


try:
    from couple.models import Anniversary
    post_save.connect(unlock_anniversary_moment_achievement, sender=Anniversary)
except ImportError:
    pass


# 用户注册时自动初始化成就
def init_user_achievements(user):
    """为新用户初始化成就"""
    # 获取所有成就
    achievements = Achievement.objects.all()
    
    # 为每个成就创建用户成就记录
    for achievement in achievements:
        UserAchievement.objects.create(
            user=user,
            achievement=achievement,
            unlocked=False,
            progress=0
        )

# 监听用户注册事件，初始化成就
@receiver(post_save, sender=User)
def create_user_achievements(sender, instance, created, **kwargs):
    if created:
        init_user_achievements(instance)



class CommunityEvent(models.Model):
    """社区活动"""
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
        db_table = 'community_event'
        ordering = ['-is_pinned', '-created_at']
        verbose_name = '社区活动'
        verbose_name_plural = '社区活动'

    def __str__(self):
        return self.title

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, '未知')


class ReportType(models.Model):
    """举报类型"""
    name = models.CharField(max_length=50, unique=True, verbose_name='举报类型名称')
    description = models.TextField(verbose_name='类型描述')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'community_report_type'
        verbose_name = '举报类型'
        verbose_name_plural = '举报类型'
        ordering = ['name']

    def __str__(self):
        return self.name


class Report(models.Model):
    """举报记录"""
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('reviewing', '审核中'),
        ('resolved', '已处理'),
        ('dismissed', '已驳回'),
    ]

    REPORT_TYPE_CHOICES = [
        ('content', '内容举报'),
        ('harassment', '骚扰举报'),
        ('spam', '垃圾信息'),
        ('inappropriate', '不当行为'),
        ('other', '其他举报'),
    ]

    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made', verbose_name='举报人')
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_received', verbose_name='被举报人')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES, verbose_name='举报类型')
    title = models.CharField(max_length=200, verbose_name='举报标题')
    description = models.TextField(verbose_name='举报描述')
    evidence = models.TextField(blank=True, null=True, verbose_name='证据信息')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='处理状态')
    
    # 关联内容
    content_type = models.CharField(max_length=50, blank=True, null=True, verbose_name='内容类型')
    content_id = models.IntegerField(blank=True, null=True, verbose_name='内容ID')
    content_title = models.CharField(max_length=200, blank=True, null=True, verbose_name='内容标题')
    
    # 处理信息
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='reports_reviewed', verbose_name='处理人')
    review_notes = models.TextField(blank=True, null=True, verbose_name='处理备注')
    action_taken = models.CharField(max_length=200, blank=True, null=True, verbose_name='处理措施')
    
    # 时间信息
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='举报时间')
    reviewed_at = models.DateTimeField(blank=True, null=True, verbose_name='处理时间')
    resolved_at = models.DateTimeField(blank=True, null=True, verbose_name='解决时间')
    
    # 其他信息
    priority = models.IntegerField(default=1, choices=[(1, '低'), (2, '中'), (3, '高')], verbose_name='优先级')
    is_urgent = models.BooleanField(default=False, verbose_name='是否紧急')

    class Meta:
        db_table = 'community_report'
        verbose_name = '举报记录'
        verbose_name_plural = '举报记录'
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return f"{self.reporter.username} 举报 {self.reported_user.username} - {self.title}"

    def get_status_display(self):
        """获取状态显示文本"""
        return dict(self.STATUS_CHOICES).get(self.status, '未知')

    def get_report_type_display(self):
        """获取举报类型显示文本"""
        return dict(self.REPORT_TYPE_CHOICES).get(self.report_type, '未知')

    def mark_as_reviewing(self, reviewer):
        """标记为审核中"""
        self.status = 'reviewing'
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.save()

    def mark_as_resolved(self, action_taken=""):
        """标记为已处理"""
        self.status = 'resolved'
        self.action_taken = action_taken
        self.resolved_at = timezone.now()
        self.save()

    def mark_as_dismissed(self, review_notes=""):
        """标记为已驳回"""
        self.status = 'dismissed'
        self.review_notes = review_notes
        self.resolved_at = timezone.now()
        self.save()


class ReportAction(models.Model):
    """举报处理措施"""
    ACTION_TYPE_CHOICES = [
        ('warning', '警告'),
        ('content_removal', '内容删除'),
        ('account_suspension', '账号暂停'),
        ('account_ban', '账号封禁'),
        ('no_action', '无需处理'),
    ]

    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='actions', verbose_name='举报记录')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPE_CHOICES, verbose_name='处理类型')
    description = models.TextField(verbose_name='处理描述')
    duration = models.IntegerField(blank=True, null=True, verbose_name='持续时间(天)')
    
    # 执行人
    executed_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='executed_actions', verbose_name='执行人')
    
    # 时间信息
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    executed_at = models.DateTimeField(blank=True, null=True, verbose_name='执行时间')
    expires_at = models.DateTimeField(blank=True, null=True, verbose_name='过期时间')
    
    # 状态
    is_executed = models.BooleanField(default=False, verbose_name='是否已执行')
    is_reverted = models.BooleanField(default=False, verbose_name='是否已撤销')

    class Meta:
        db_table = 'community_report_action'
        verbose_name = '举报处理措施'
        verbose_name_plural = '举报处理措施'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.report.title} - {self.get_action_type_display()}"

    def execute_action(self, executed_by):
        """执行处理措施"""
        self.executed_by = executed_by
        self.executed_at = timezone.now()
        self.is_executed = True
        
        # 如果设置了持续时间，计算过期时间
        if self.duration:
            self.expires_at = self.executed_at + timezone.timedelta(days=self.duration)
        
        self.save()

    def revert_action(self):
        """撤销处理措施"""
        self.is_reverted = True
        self.save()


class ReportStatistics(models.Model):
    """举报统计"""
    date = models.DateField(unique=True, verbose_name='日期')
    total_reports = models.IntegerField(default=0, verbose_name='总举报数')
    pending_reports = models.IntegerField(default=0, verbose_name='待处理举报数')
    resolved_reports = models.IntegerField(default=0, verbose_name='已处理举报数')
    dismissed_reports = models.IntegerField(default=0, verbose_name='已驳回举报数')
    
    # 按类型统计
    content_reports = models.IntegerField(default=0, verbose_name='内容举报数')
    harassment_reports = models.IntegerField(default=0, verbose_name='骚扰举报数')
    spam_reports = models.IntegerField(default=0, verbose_name='垃圾信息举报数')
    other_reports = models.IntegerField(default=0, verbose_name='其他举报数')
    
    # 处理效率
    avg_resolution_time = models.FloatField(default=0.0, verbose_name='平均处理时间(小时)')
    resolution_rate = models.FloatField(default=0.0, verbose_name='处理率')

    class Meta:
        db_table = 'community_report_statistics'
        verbose_name = '举报统计'
        verbose_name_plural = '举报统计'
        ordering = ['-date']

    def __str__(self):
        return f"举报统计 - {self.date}"

    def update_statistics(self):
        """更新统计数据"""
        from datetime import timedelta
        
        # 获取当天的举报数据
        reports = Report.objects.filter(
            created_at__date=self.date
        )
        
        self.total_reports = reports.count()
        self.pending_reports = reports.filter(status='pending').count()
        self.resolved_reports = reports.filter(status='resolved').count()
        self.dismissed_reports = reports.filter(status='dismissed').count()
        
        # 按类型统计
        self.content_reports = reports.filter(report_type='content').count()
        self.harassment_reports = reports.filter(report_type='harassment').count()
        self.spam_reports = reports.filter(report_type='spam').count()
        self.other_reports = reports.filter(report_type='other').count()
        
        # 计算处理率和平均处理时间
        resolved_reports = reports.filter(status='resolved')
        if resolved_reports.exists():
            total_resolution_time = 0
            count = 0
            
            for report in resolved_reports:
                if report.resolved_at and report.created_at:
                    resolution_time = (report.resolved_at - report.created_at).total_seconds() / 3600
                    total_resolution_time += resolution_time
                    count += 1
            
            if count > 0:
                self.avg_resolution_time = total_resolution_time / count
            
            if self.total_reports > 0:
                self.resolution_rate = (self.resolved_reports / self.total_reports) * 100
        
        self.save()