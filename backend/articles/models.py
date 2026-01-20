from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from core.models import User

def get_article_image_path(instance, filename):
    """文章图片上传路径：articles/images/年份/月份/日期"""
    import os
    from datetime import datetime
    now = datetime.now()
    return os.path.join('articles', 'images', str(now.year), str(now.month), str(now.day), filename)

def get_column_cover_path(instance, filename):
    """专栏封面图片上传路径：articles/column_bg/"""
    import os
    return os.path.join('articles', 'column_bg', filename)

class OfficialColumn(models.Model):
    """官方专栏模型"""
    CATEGORY_CHOICES = [
        ('love_growth', '恋爱成长手册'),
        ('diary_inspiration', '日记灵感库'),
        ('festival_special', '节日特辑'),
        ('platform_activity', '平台活动通知'),
        ('other', '其他'),
    ]
    
    name = models.CharField(max_length=100, unique=True, verbose_name='专栏名称')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='专栏标识')
    description = models.TextField(blank=True, null=True, verbose_name='专栏简介')
    cover_image = models.ImageField(upload_to=get_column_cover_path, blank=True, null=True, verbose_name='专栏封面图')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name='专栏分类')
    subscriber_count = models.IntegerField(default=0, verbose_name='订阅人数')
    view_count = models.IntegerField(default=0, verbose_name='浏览量')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '官方专栏'
        verbose_name_plural = '官方专栏管理'
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name

class ColumnArticle(models.Model):
    """专栏文章模型"""
    column = models.ForeignKey(OfficialColumn, on_delete=models.CASCADE, related_name='articles', verbose_name='所属专栏')
    title = models.CharField(max_length=200, verbose_name='文章标题')
    content = models.TextField(verbose_name='文章内容')
    cover_image = models.ImageField(upload_to=get_article_image_path, blank=True, null=True, verbose_name='文章封面图')
    view_count = models.IntegerField(default=0, verbose_name='浏览量')
    like_count = models.IntegerField(default=0, verbose_name='点赞数')
    comment_count = models.IntegerField(default=0, verbose_name='评论数')
    published_at = models.DateTimeField(auto_now_add=True, verbose_name='发布时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '专栏文章'
        verbose_name_plural = '专栏文章管理'
        ordering = ['-published_at']
    
    def __str__(self):
        return self.title

class ColumnComment(models.Model):
    """专栏评论模型"""
    article = models.ForeignKey(ColumnArticle, on_delete=models.CASCADE, related_name='comments', verbose_name='所属文章')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='column_comments', verbose_name='评论用户')
    content = models.TextField(max_length=500, verbose_name='评论内容')
    like_count = models.IntegerField(default=0, verbose_name='点赞数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '专栏评论'
        verbose_name_plural = '专栏评论管理'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'评论 by {self.user.username} on {self.article.title}'

class ArticleLike(models.Model):
    """文章点赞模型"""
    article = models.ForeignKey(ColumnArticle, on_delete=models.CASCADE, related_name='likes', verbose_name='所属文章')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='article_likes', verbose_name='点赞用户')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '文章点赞'
        verbose_name_plural = '文章点赞管理'
        unique_together = ('article', 'user')
    
    def __str__(self):
        return f'Like by {self.user.username} on {self.article.title}'

class ColumnSubscription(models.Model):
    """专栏订阅模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='column_subscriptions', verbose_name='订阅用户')
    column = models.ForeignKey(OfficialColumn, on_delete=models.CASCADE, related_name='subscriptions', verbose_name='订阅专栏')
    is_subscribed = models.BooleanField(default=True, verbose_name='是否订阅')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '专栏订阅'
        verbose_name_plural = '专栏订阅管理'
        unique_together = ('user', 'column')
    
    def __str__(self):
        return f'{self.user.username} subscribed to {self.column.name}'


# 信号处理函数
@receiver(post_delete, sender=ColumnArticle)
def update_column_view_count(sender, instance, **kwargs):
    """更新专栏的浏览量（所有文章浏览量之和）"""
    column = instance.column
    # 计算专栏下所有文章的浏览量之和
    total_views = ColumnArticle.objects.filter(column=column).aggregate(total=models.Sum('view_count'))['total'] or 0
    column.view_count = total_views
    column.save()


@receiver(post_save, sender=ArticleLike)
@receiver(post_delete, sender=ArticleLike)
def update_article_like_count(sender, instance, **kwargs):
    """更新文章的点赞数"""
    article = instance.article
    # 计算文章的点赞数
    article.like_count = ArticleLike.objects.filter(article=article).count()
    article.save()


@receiver(post_save, sender=ColumnComment)
@receiver(post_delete, sender=ColumnComment)
def update_article_comment_count(sender, instance, **kwargs):
    """更新文章的评论数"""
    article = instance.article
    # 计算文章的评论数
    article.comment_count = ColumnComment.objects.filter(article=article).count()
    article.save()