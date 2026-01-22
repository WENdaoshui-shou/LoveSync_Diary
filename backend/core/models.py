from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.signals import user_logged_in
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
        default='userAvatar/defult_user.png'
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


# VIP会员模型
class VIPMember(models.Model):
    """VIP会员模型"""
    VIP_LEVELS = [
        ('normal', 'Ⅰ'),
        ('bronze', 'Ⅱ'),
        ('silver', 'Ⅲ'),
        ('diamond', 'Ⅳ'),
        ('king', 'Ⅴ'),
        ('god', 'Ⅵ'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vip')
    level = models.CharField(max_length=20, choices=VIP_LEVELS, default='normal', verbose_name='VIP等级')
    start_date = models.DateTimeField(auto_now_add=True, verbose_name='开通时间')
    end_date = models.DateTimeField(null=True, blank=True, verbose_name='到期时间')
    is_active = models.BooleanField(default=False, verbose_name='是否活跃')
    renewal_count = models.IntegerField(default=0, verbose_name='续费次数')
    total_recharge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='累计充值金额')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = 'VIP会员'
        verbose_name_plural = 'VIP会员管理'
        ordering = ['-level']
    
    def __str__(self):
        return f'{self.user.username} - {self.get_level_display()}'
    
    def get_level_color(self):
        """获取VIP等级对应的颜色"""
        color_map = {
                'normal': 'linear-gradient(135deg, #F3F4F6, #E5E7EB)', 
                'bronze': 'linear-gradient(135deg, #8B4513, #FFD700)',  
                'silver': 'linear-gradient(135deg, #C0C0C0, #333333)', 
                'diamond': 'linear-gradient(135deg, #00BFFF, #006400)',
                'king': 'linear-gradient(135deg, #FF6347, #FFB6C1)',
                'god': 'linear-gradient(135deg, #722ED1, #FF6B8B)'
                }
        return color_map.get(self.level, 'linear-gradient(135deg, #F3F4F6, #E5E7EB)')
    
    def get_level_text_color(self):
        """获取VIP等级对应的文字颜色"""
        text_color_map = {
            'bronze': '#fff',
            'silver': '#fff',
            'diamond': '#fff',
            'king': '#fff',
            'god': '#fff',
        }
        return text_color_map.get(self.level, '#666')
    
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
        """检查VIP状态并处理到期情况"""
        from django.utils import timezone
        now = timezone.now()
        if self.end_date and self.end_date < now:
            self.is_active = False
            # VIP到期后，保持等级不变，但标记为非活跃状态
            self.save()
        return self.is_active
    
    def update_vip_level(self):
        """根据累计充值金额更新VIP等级"""
        total = self.total_recharge
        new_level = 'normal'
        
        # 根据累计充值金额确定VIP等级
        if total >= 1000:
            new_level = 'god'  # 神VIP：累计充值1000元以上
        elif total >= 500:
            new_level = 'king'  # 国王VIP：累计充值500-999元
        elif total >= 200:
            new_level = 'diamond'  # 钻石VIP：累计充值200-499元
        elif total >= 100:
            new_level = 'silver'  # 白银VIP：累计充值100-199元
        elif total >= 50:
            new_level = 'bronze'  # 青铜VIP：累计充值50-99元
        
        # 如果等级发生变化，更新等级
        if self.level != new_level:
            self.level = new_level
            self.save()
        
        return new_level

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


# VIP充值订单模型
class VIPOrder(models.Model):
    """VIP充值订单模型"""
    STATUS_CHOICES = [
        ('pending', '待支付'),
        ('success', '支付成功'),
        ('failed', '支付失败'),
        ('cancelled', '已取消'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vip_orders', verbose_name='用户')
    amount = models.IntegerField(verbose_name='充值金额')
    duration = models.IntegerField(verbose_name='充值时长(天)')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='订单状态')
    order_number = models.CharField(max_length=50, unique=True, verbose_name='订单号')
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='支付时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = 'VIP充值订单'
        verbose_name_plural = 'VIP充值订单管理'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'订单 {self.order_number} - {self.get_status_display()}'

# 成就系统模型
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

# 用户注册时自动创建 Profile 模型
@receiver(post_save, sender=User)
def create_and_save_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        # 为新用户创建默认VIP记录
        VIPMember.objects.create(user=instance)
        # 为新用户初始化成就
        init_user_achievements(instance)
    # 每次保存用户时都保存 Profile
    instance.profile.save()

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

# 监听情侣绑定事件，解锁"初次相遇"成就
@receiver(post_save, sender=Profile)
def unlock_first_meeting_achievement(sender, instance, created, **kwargs):
    """当用户绑定情侣关系时，解锁"初次相遇"成就"""
    if not created and instance.couple:
        if instance.couple_joined_at:
            try:
                achievement = Achievement.objects.get(title='初次相遇')
                user_achievement, created = UserAchievement.objects.get_or_create(
                    user=instance.user,
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
@receiver(post_save, sender=Profile)
def unlock_anniversary_achievement(sender, instance, created, **kwargs):
    """当情侣关系满一周年时，解锁"一周年纪念"成就"""
    if not created and instance.couple and instance.couple_joined_at:
        # 计算情侣关系持续时间
        joined_at = instance.couple_joined_at
        now = timezone.now()
        years = now.year - joined_at.year
        
        # 检查是否满一周年
        if years >= 1:
            try:
                achievement = Achievement.objects.get(title='一周年纪念')
                # 获取用户成就记录
                user_achievement, created = UserAchievement.objects.get_or_create(
                    user=instance.user,
                    achievement=achievement
                )
                # 解锁成就
                user_achievement.unlock()
            except Achievement.DoesNotExist:
                pass

# 监听动态和评论事件，解锁"社交达人"成就
def unlock_social_master_achievement(sender, instance, created, **kwargs):
    """当用户发布动态或评论时，更新"社交达人"成就"""
    if created:
        user = instance.user
        try:
            achievement = Achievement.objects.get(title='社交达人')
            # 获取用户成就记录
            user_achievement, created = UserAchievement.objects.get_or_create(
                user=user,
                achievement=achievement
            )
            
            # 计算用户的社交活动数量
            social_count = 0
            
            # 计算动态数量
            try:
                from moment.models import Moment
                social_count += Moment.objects.filter(user=user).count()
            except ImportError:
                pass
            
            # 计算评论数量（假设存在评论模型）
            try:
                from moment.models import Comment
                social_count += Comment.objects.filter(user=user).count()
            except ImportError:
                pass
            
            # 更新进度
            progress = min(social_count * 5, 100)  # 每20个社交活动解锁
            user_achievement.update_progress(progress)
            
            if progress >= 100:
                user_achievement.unlock()
        except Achievement.DoesNotExist:
            pass

# 注册其他成就信号
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

try:
    from moment.models import Moment
    post_save.connect(unlock_social_master_achievement, sender=Moment)
except ImportError:
    pass

try:
    from moment.models import Comment
    post_save.connect(unlock_social_master_achievement, sender=Comment)
except ImportError:
    pass
