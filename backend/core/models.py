from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from django.utils import timezone


# 用户
class User(AbstractUser):
    username = models.CharField(max_length=11, unique=True, db_index=True, verbose_name='手机号')
    name = models.CharField(max_length=30, default='用户名')
    email = models.EmailField(max_length=30, null=True, blank=True)
    phone_verified = models.BooleanField(default=False, verbose_name='手机号已验证')
    email_verified = models.BooleanField(default=False, verbose_name='邮箱已验证')
    REQUIRED_FIELDS = []


# 关注关系模型
class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followed')

    def __str__(self):
        return f'{self.follower.username} 关注了 {self.followed.username}'


GENDER_CHOICES = [
    ('female', '女'),
    ('male', '男'),
    ('other', '保密'),
]

LOCATION_CHOICES = [
    ('北京市', '北京市'),
    ('天津市', '天津市'),
    ('重庆市', '重庆市'),
    ('上海市', '上海市'),
]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    userAvatar = models.ImageField(
        upload_to='userAvatar/',
        blank=True,
        null=True,
        default='userAvatar/OIP-C.jpg'
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='other', verbose_name='性别')
    birth_date = models.DateField(null=True, blank=True, verbose_name='出生日期')
    location = models.CharField(max_length=100, choices=LOCATION_CHOICES, null=True, blank=True, verbose_name='所在地')
    bio = models.TextField(max_length=500, null=True, blank=True, verbose_name='个人简介')

    # 情侣关系字段
    couple = models.OneToOneField(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='partner',
    )
    couple_joined_at = models.DateTimeField(null=True, blank=True, verbose_name='绑定时间')
    couple_code = models.CharField(max_length=10, blank=True, null=True, unique=True, verbose_name='情侣邀请码')
    couple_pending = models.OneToOneField(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='pending_partner',
    )
    
    # 通知设置
    notification_sound = models.BooleanField(default=True, verbose_name='开启通知声音')
    notification_vibration = models.BooleanField(default=True, verbose_name='开启震动提醒')
    do_not_disturb = models.BooleanField(default=False, verbose_name='夜间免打扰')
    couple_messages = models.BooleanField(default=True, verbose_name='情侣消息通知')
    community_messages = models.BooleanField(default=True, verbose_name='社区消息通知')
    system_messages = models.BooleanField(default=True, verbose_name='系统消息通知')
    comments_replies = models.BooleanField(default=True, verbose_name='评论和回复通知')
    likes_favorites = models.BooleanField(default=True, verbose_name='点赞和收藏通知')
    anniversary_reminders = models.BooleanField(default=True, verbose_name='纪念日提醒')
    couple_activity_recommendations = models.BooleanField(default=True, verbose_name='情侣活动推荐')
    hot_topic_reminders = models.BooleanField(default=False, verbose_name='热门话题提醒')
    promotion_push = models.BooleanField(default=False, verbose_name='优惠活动推送')
    
    # 隐私设置
    profile_visibility = models.CharField(max_length=20, choices=[('everyone', '所有人可见'), ('friends', '仅好友可见'), ('private', '仅自己可见')], default='everyone', verbose_name='个人主页可见性')
    show_online_status = models.BooleanField(default=True, verbose_name='显示在线状态')
    allow_search = models.BooleanField(default=True, verbose_name='允许被搜索')
    show_location = models.BooleanField(default=False, verbose_name='显示地理位置')
    moments_visibility = models.CharField(max_length=20, choices=[('everyone', '所有人可见'), ('friends', '仅好友可见'), ('private', '仅自己可见')], default='everyone', verbose_name='动态可见性')
    album_visibility = models.CharField(max_length=20, choices=[('everyone', '所有人可见'), ('friends', '仅好友可见'), ('private', '仅自己可见')], default='friends', verbose_name='相册可见性')
    
    # 账号安全设置
    two_factor_auth = models.BooleanField(default=False, verbose_name='双因素认证')
    login_notification = models.BooleanField(default=True, verbose_name='登录通知')
    session_management = models.BooleanField(default=True, verbose_name='会话管理')
    
    # 外观设置
    theme = models.CharField(max_length=20, choices=[('light', '浅色主题'), ('dark', '深色主题'), ('system', '跟随系统')], default='light', verbose_name='主题')
    font_size = models.CharField(max_length=20, choices=[('small', '小'), ('medium', '中'), ('large', '大')], default='medium', verbose_name='字体大小')
    interface_style = models.CharField(max_length=20, choices=[('modern', '现代'), ('classic', '经典')], default='modern', verbose_name='界面风格')

    def __str__(self):
        return f"{self.user.username} 的个人设置"

    class Meta:
        verbose_name = '用户设置'
        verbose_name_plural = '用户设置'

    def save(self, *args, **kwargs):
        # 生成情侣邀请码
        if not self.couple_code:
            self.couple_code = self.generate_couple_code()
        super().save(*args, **kwargs)

    def generate_couple_code(self):
        """生成唯一的6位数字邀请码"""
        import random
        while True:
            code = f"{random.randint(100000, 999999)}"
            if not Profile.objects.filter(couple_code=code).exists():
                return code

    def send_couple_request(self, target_profile):
        """发送情侣绑定请求"""
        # 检查是否已经是情侣
        if self.couple == target_profile:
            raise ValidationError("你们已经是情侣关系了")

        # 检查对方是否已经有情侣
        if target_profile.couple:
            raise ValidationError("对方已经有情侣了")

        # 检查是否有未处理的请求
        if self.couple_pending or target_profile.couple_pending:
            raise ValidationError("有未处理的情侣请求")

        # 发送请求 - 只设置一个方向，Django会自动处理反向关系
        self.couple_pending = target_profile
        
        # 只保存发送请求的用户
        self.save()
        return True

    def accept_couple_request(self):
        """接受情侣绑定请求"""
        # 对于收到请求的用户，请求信息存储在pending_partner中
        if not self.pending_partner:
            raise ValidationError("没有待处理的情侣请求")

        requester = self.pending_partner

        # 建立情侣关系
        self.couple = requester
        requester.couple = self

        # 记录绑定时间
        now = timezone.now()
        self.couple_joined_at = now
        requester.couple_joined_at = now

        # 清除待处理请求
        requester.couple_pending = None
        self.save()
        requester.save()

        return True

    def reject_couple_request(self):
        """拒绝情侣绑定请求"""
        # 对于收到请求的用户，请求信息存储在pending_partner中
        if not self.pending_partner:
            raise ValidationError("没有待处理的情侣请求")

        requester = self.pending_partner
        requester.couple_pending = None

        self.save()
        requester.save()

        return True

    def break_up(self):
        """解除情侣关系"""
        if not self.couple:
            raise ValidationError(("你没有情侣关系"))

        partner = self.couple

        # 记录关系结束时间
        CoupleRelationHistory.objects.create(
            user1=self.user,
            user2=partner.user,
            started_at=self.couple_joined_at,
            ended_at=timezone.now()
        )

        # 解除关系
        self.couple = None
        partner.couple = None

        # 清除绑定时间
        self.couple_joined_at = None
        partner.couple_joined_at = None

        # 保存双方
        self.save()
        partner.save()

        return True


# 情侣关系历史记录
class CoupleRelationHistory(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='relation_history_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='relation_history_as_user2')
    started_at = models.DateTimeField(verbose_name='开始时间')
    ended_at = models.DateTimeField(verbose_name='结束时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='记录创建时间')

    class Meta:
        verbose_name = '情侣关系历史'
        verbose_name_plural = '情侣关系历史记录'
        ordering = ['-ended_at']

    def __str__(self):
        return f"{self.user1.username} 与 {self.user2.username} 的关系历史"


# 验证码模型
class VerificationCode(models.Model):
    TYPE_CHOICES = [
        ('phone', '手机号'),
        ('email', '邮箱'),
    ]
    
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name='验证类型')
    target = models.CharField(max_length=50, verbose_name='目标')  # 手机号或邮箱
    code = models.CharField(max_length=6, verbose_name='验证码')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    expires_at = models.DateTimeField(verbose_name='过期时间')
    is_used = models.BooleanField(default=False, verbose_name='是否已使用')
    
    class Meta:
        verbose_name = '验证码'
        verbose_name_plural = '验证码记录'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.type} 验证码: {self.target} - {self.code}"


# 爱情故事时间轴模型
class LoveStoryTimeline(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='love_story_timeline')
    title = models.CharField(max_length=100, verbose_name='事件标题')
    description = models.TextField(verbose_name='事件描述')
    date = models.DateField(verbose_name='事件日期')
    image = models.ImageField(upload_to='love_story_images/', null=True, blank=True, verbose_name='事件图片')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.user.username} 的爱情故事: {self.title}'


# 音乐播放器模型
class MusicPlayer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='music_player')
    title = models.CharField(max_length=100, verbose_name='歌曲标题')
    artist = models.CharField(max_length=100, verbose_name='歌手')
    album_cover = models.ImageField(upload_to='music_covers/', null=True, blank=True, verbose_name='专辑封面')
    audio_file = models.FileField(upload_to='music_files/', null=True, blank=True, verbose_name='音频文件')
    is_currently_playing = models.BooleanField(default=False, verbose_name='是否正在播放')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} 的音乐: {self.title} - {self.artist}'


# 情侣问答模型
class CoupleQuiz(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='couple_quizzes')
    question = models.TextField(verbose_name='问题')
    correct_answer = models.CharField(max_length=100, verbose_name='正确答案')
    options = models.JSONField(verbose_name='选项列表')  # 使用JSONField存储选项
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} 的情侣问答: {self.question}'




# VIP会员模型
class VIPMember(models.Model):
    """VIP会员模型"""
    VIP_LEVELS = [
        ('normal', '普通会员'),
        ('bronze', '青铜VIP'),
        ('silver', '白银VIP'),
        ('gold', '黄金VIP'),
        ('platinum', '铂金VIP'),
        ('diamond', '钻石VIP'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vip')
    level = models.CharField(max_length=20, choices=VIP_LEVELS, default='normal', verbose_name='VIP等级')
    start_date = models.DateTimeField(auto_now_add=True, verbose_name='开通时间')
    end_date = models.DateTimeField(null=True, blank=True, verbose_name='到期时间')
    is_active = models.BooleanField(default=False, verbose_name='是否活跃')
    renewal_count = models.IntegerField(default=0, verbose_name='续费次数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = 'VIP会员'
        verbose_name_plural = 'VIP会员管理'
        ordering = ['-level']
    
    def __str__(self):
        return f'{self.user.username} - {self.get_level_display()}'
    
    def activate_vip(self, duration_days=30):
        """激活VIP会员"""
        from django.utils import timezone
        now = timezone.now()
        self.start_date = now
        self.end_date = now + timezone.timedelta(days=duration_days)
        self.is_active = True
        self.renewal_count += 1
        self.save()
        return True
    
    def renew_vip(self, duration_days=30):
        """续费VIP会员"""
        from django.utils import timezone
        now = timezone.now()
        if self.end_date and self.end_date > now:
            # 如果VIP还在有效期内，从到期时间开始续费
            self.end_date += timezone.timedelta(days=duration_days)
        else:
            # 如果VIP已经过期，从现在开始续费
            self.start_date = now
            self.end_date = now + timezone.timedelta(days=duration_days)
        self.is_active = True
        self.renewal_count += 1
        self.save()
        return True
    
    def check_vip_status(self):
        """检查VIP状态"""
        from django.utils import timezone
        now = timezone.now()
        if self.end_date and self.end_date < now:
            self.is_active = False
            self.save()
        return self.is_active

# VIP特权模型
class VIPPrivilege(models.Model):
    """VIP特权模型"""
    name = models.CharField(max_length=100, verbose_name='特权名称')
    description = models.TextField(verbose_name='特权描述')
    required_level = models.CharField(max_length=20, choices=VIPMember.VIP_LEVELS, verbose_name='所需VIP等级')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = 'VIP特权'
        verbose_name_plural = 'VIP特权管理'
        ordering = ['-required_level']
    
    def __str__(self):
        return f'{self.name} - {self.get_required_level_display()}'

# 用户注册时自动创建 Profile 模型
@receiver(post_save, sender=User)
def create_and_save_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        # 为新用户创建默认VIP记录
        VIPMember.objects.create(user=instance)
    # 每次保存用户时都保存 Profile
    instance.profile.save()
