from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


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


# 用户
class UserManager(BaseUserManager):
    def create_user(self, username, password=None, phone=None, email=None, userAvatar=None):
        if not username:
            raise ValueError('用户必须有用户名')

        user = self.model(
            username=username,
            phone=phone,
            email=self.normalize_email(email),  # 规范化邮箱
            userAvatar=userAvatar
        )
        user.set_password(password)  # 哈希密码
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, email=None):
        user = self.create_user(
            username=username,
            password=password,
            email=email
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=128)  # 增加长度以存储哈希密码
    phone = models.CharField(max_length=11, null=True)
    email = models.EmailField(max_length=30, null=True)  # 使用 EmailField 自动验证
    userAvatar = models.CharField(max_length=128, null=True)
