from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from django.utils import timezone


# CustomUser：扩展了 Django 的用户模型，添加了 couple 字段用于关联情侣关系。
# Diary：存储双人日记的信息，包括作者、标题、内容和创建时间。
# Moment：存储情侣的动态信息，包括用户、内容、图片、点赞数、评论数和创建时间。
# PhotoAlbum：存储情侣相册的信息，包括用户、照片、描述和创建时间。
# Favorite：存储用户的收藏信息，包括用户、收藏类型和收藏项的 ID。
# Anniversary：存储纪念日提醒的信息，包括用户、纪念日名称、日期和是否提醒。
# GiftRecommendation：存储礼物推荐的信息，包括用户、礼物名称、描述和价格。
# CoupleLocation：存储情侣地点的信息，包括用户、地点名称、地址和描述。
# LoveTest：存储爱情测试的信息，包括用户、测试名称、结果和创建时间。
# Message：存储用户之间的消息信息，包括发送者、接收者、内容、创建时间和是否已读。
# Product：存储商品信息，包括名称、描述、价格和图片。


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


# 评论
class Comment(models.Model):
    moment = models.ForeignKey(Moment, on_delete=models.CASCADE, related_name='comment_set')  # 修改关联名称
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
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
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='商品图片')
    rating = models.FloatField(default=0, verbose_name='商品评分')
    num_reviews = models.IntegerField(default=0, verbose_name='评论数量')
    category = models.CharField(max_length=100, verbose_name='商品类别')
    monthly_sales = models.IntegerField(default=0, verbose_name='月销量')

    def __str__(self):
        return self.name
