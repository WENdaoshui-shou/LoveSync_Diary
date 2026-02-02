from django.db import models
from core.models import User


# 发布动态
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)  # 标签名称（唯一）
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Moment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='moments')
    content = models.TextField(verbose_name='动态内容')
    likes = models.IntegerField(default=0, verbose_name='点赞数')
    comments = models.IntegerField(default=0, verbose_name='评论数')
    favorites = models.IntegerField(default=0, verbose_name='收藏数')
    view_count = models.IntegerField(default=0, verbose_name='浏览数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    is_shared = models.BooleanField(default=False)  
    tags = models.ManyToManyField(Tag, blank=True, related_name='moments')  

    def get_hot_score(self):
        """计算热度值"""
        # 热度计算公式：点赞权重2，评论权重3，浏览权重1
        return self.likes * 2 + self.comments * 3 + self.view_count * 1

    class Meta:
        verbose_name = '社区动态'
        verbose_name_plural = '社区动态'

    def __str__(self):
        return f'{self.user.username} 的动态 - {self.created_at}'


class MomentImage(models.Model):
    moment = models.ForeignKey(Moment, on_delete=models.CASCADE, related_name='moment_images')
    image = models.ImageField(upload_to='moment_images/%Y/%m/%d/')

    def __str__(self):
        return f'图片 for {self.moment}'


# 评论
class Comment(models.Model):
    moment = models.ForeignKey(Moment, on_delete=models.CASCADE, related_name='comment_set')  # 修改关联名称
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} 对 {self.parent.user.username if self.parent else '动态'} 的评论: {self.content[:20]}"


# 点赞
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_likes')
    moment = models.ForeignKey(Moment, on_delete=models.CASCADE, related_name='moment_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'moment')  # 确保每个用户只能点赞一次

    def __str__(self):
        return f'{self.user.username} 点赞了 {self.moment}'



