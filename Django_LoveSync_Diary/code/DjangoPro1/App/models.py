from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from django.utils import timezone


# 用户
class User(AbstractUser):
    username = models.CharField(max_length=11, unique=True)
    password = models.CharField(max_length=128)  # 增加长度以存储哈希密码
    name = models.CharField(max_length=30, default='用户名')
    email = models.EmailField(max_length=30, null=True)  # 使用 EmailField 自动验证

    USERNAME_FIELD = 'username'


# 发布动态
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)  # 标签名称（唯一）
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Moment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='moments')
    content = models.TextField(verbose_name='动态内容')
    likes = models.IntegerField(default=0, verbose_name='点赞数', db_default=0)
    comments = models.IntegerField(default=0, verbose_name='评论数', db_default=0)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    is_shared = models.BooleanField(default=False)  # 新增字段，表示是否被分享
    tags = models.ManyToManyField(Tag, blank=True, related_name='moments')  # 添加标签多对多字段

    def __str__(self):
        return f'{self.user.username} 的动态 - {self.created_at}'


class MomentImage(models.Model):
    moment = models.ForeignKey(Moment, on_delete=models.CASCADE, related_name='moment_images')
    image = models.ImageField(upload_to='moment_images/%Y/%m/%d/')

    def __str__(self):
        return f'图片 for {self.moment}'


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

    def __str__(self):
        return f"{self.user.username} 的个人设置"

    class Meta:
        verbose_name = '用户设置'
        verbose_name_plural = '用户设置'

    def save(self, *args, **kwargs):
        # 生成情侣邀请码（如果没有）
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
            raise ValidationError(_("你们已经是情侣关系了"))

        # 检查对方是否已经有情侣
        if target_profile.couple:
            raise ValidationError(_("对方已经有情侣了"))

        # 检查是否有未处理的请求
        if self.couple_pending or target_profile.couple_pending:
            raise ValidationError(("有未处理的情侣请求"))

        # 发送请求
        self.couple_pending = target_profile
        self.save()
        return True

    def accept_couple_request(self):
        """接受情侣绑定请求"""
        if not self.couple_pending:
            requester = self.couple_pending

        # 建立情侣关系
        self.couple = requester
        requester.couple = self

        # 记录绑定时间
        now = timezone.now()
        self.couple_joined_at = now
        requester.couple_joined_at = now

        # 清除待处理请求
        self.couple_pending = None
        requester.couple_pending = None

        # 保存双方
        self.save()
        requester.save()

        return True

    def reject_couple_request(self):
        """拒绝情侣绑定请求"""
        if not self.couple_pending:
            raise ValidationError(("没有待处理的情侣请求"))

        requester = self.couple_pending
        self.couple_pending = None
        requester.couple_pending = None

        self.save()
        requester.save()

        return True

    def break_up(self):
        """解除情侣关系"""
        if not self.couple:
            raise ValidationError(("你没有情侣关系"))

        partner = self.couple

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

    def __str__(self):
        return f"{self.user.username} 的个人设置"

    class Meta:
        verbose_name = '用户设置'
        verbose_name_plural = '用户设置'


#  用户注册时自动创建 Profile 模型
@receiver(post_save, sender=User)
def create_and_save_user_profile(sender, instance, created, **kwargs):
    if created:
        # 创建 Profile 对象
        Profile.objects.create(user=instance)
    # 每次保存用户时都保存 Profile（可选，根据需要保留）
    instance.profile.save()


# 日记
class Note(models.Model):
    MOOD_CHOICES = [
        ('happy', '开心'),
        ('heart', '心动'),
        ('laugh', '欢乐'),
        ('sad', '难过'),
        ('angry', '生气'),
        ('calm', '平静'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_note')
    context = models.TextField(max_length=1000, verbose_name='日记内容')
    created_at = models.DateTimeField(verbose_name='创建时间', default=timezone.now)
    mood = models.CharField(default='happy', max_length=10, choices=MOOD_CHOICES, verbose_name='心情')
    is_shared = models.BooleanField(default=False, verbose_name='是否共享')

    def __str__(self):
        return f"{self.user.username}的日记 #{self.id}"

    # 获取心情对应的颜色（用于前端样式）
    def get_mood_color(self):
        color_mapping = {
            'happy': '#48BB78',
            'heart': '#ED8936',
            'laugh': '#ECC94B',
            'sad': '#718096',
            'angry': '#E53E3E',
            'calm': '#4299E1',
        }
        return color_mapping.get(self.mood, '#81E67F')

    # 获取心情对应的图标（用于前端显示）
    def get_mood_icon(self):
        icon_mapping = {
            'happy': '😊',
            'heart': '❤️',
            'laugh': '😆',
            'sad': '😢',
            'angry': '😤',
            'calm': '😐',
        }
        return icon_mapping.get(self.mood, '😊')

    # 获取心情的显示文本（用于前端标签）
    def get_mood_display_text(self):
        display_mapping = {
            'happy': '开心的一天',
            'heart': '心动时刻',
            'laugh': '欢乐时刻',
            'sad': '难过时刻',
            'angry': '生气时刻',
            'calm': '安静时刻',
        }
        return display_mapping.get(self.mood, '开心的一天')

    # 获取心情对应的CSS类名（用于前端样式）
    def get_mood_css_class(self):
        return self.mood


class NoteImage(models.Model):
    notemoment = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='note_images')
    noteimage = models.ImageField(upload_to='note_images/%Y/%m/%d/', verbose_name='日记图片')

    def __str__(self):
        return f"日记 #{self.notemoment.id} 的图片"


# 评论
class Comment(models.Model):
    moment = models.ForeignKey(Moment, on_delete=models.CASCADE, related_name='comment_set')  # 修改关联名称
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='note_likes', default="")
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} 对 {self.parent.user.username if self.parent else '动态'} 的评论: {self.content[:20]}"


class Photo(models.Model):
    """照片模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='photos/%Y/%m/%d/')
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo by {self.user.username} at {self.uploaded_at}"

    class Meta:
        ordering = ['-uploaded_at']


class Product(models.Model):

    def generate_product_id():
        return str(int(timezone.now().timestamp())) + '-' + str(uuid.uuid4())

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='商品ID')
    name = models.CharField(max_length=200, verbose_name='商品名称')
    description = models.TextField(verbose_name='商品描述', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品价格')
    old_price = models.DecimalField(max_digits=10, decimal_places=2, default=99, verbose_name='商品原价')
    image = models.ImageField(
        upload_to="products/id/",  # 使用自定义路径函数
        blank=True,
        null=True,
        verbose_name='商品图片'
    )
    rating = models.FloatField(default=0, verbose_name='商品评分')
    num_reviews = models.IntegerField(default=0, verbose_name='评论数量')
    category = models.CharField(max_length=100, verbose_name='商品类别')
    monthly_sales = models.IntegerField(default=0, verbose_name='月销量')
    product_stock = models.IntegerField(default=0, verbose_name='库存')

    def __str__(self):
        return self.name


class CartItem(models.Model):
    """购物车数据持久化模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product')  # 同一用户的同一商品唯一


class CollaborativeDocument(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField(default='')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    couple = models.OneToOneField('App.Profile', on_delete=models.SET_NULL, null=True, blank=True)  # 关联情侣关系
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class DocumentOperation(models.Model):
    """记录文档操作历史，用于冲突解决"""
    document = models.ForeignKey(CollaborativeDocument, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    operation_type = models.CharField(max_length=10, choices=[('insert', '插入'), ('delete', '删除')])
    position = models.IntegerField()
    text = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    revision = models.IntegerField(default=0)  # 操作版本号

    def to_operation(self):
        """转换为OT算法可用的Operation对象"""
        from .ot import Operation
        return Operation(
            op_type=self.operation_type,
            position=self.position,
            text=self.text
        )
