from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Index
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone

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
