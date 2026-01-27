from django.db import models
from core.models import User


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
    created_at = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    mood = models.CharField(default='happy', max_length=10, choices=MOOD_CHOICES, verbose_name='心情')
    is_shared = models.BooleanField(default=False, verbose_name='是否共享')
    likes = models.IntegerField(default=0, verbose_name='点赞数')
    comments = models.IntegerField(default=0, verbose_name='评论数')
    


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
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='comment_set')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='note_comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField(max_length=500, verbose_name='评论内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        ordering = ['-created_at']
        verbose_name = '日记评论'
        verbose_name_plural = '日记评论'

    def __str__(self):
        return f"{self.user.username} 对日记 #{self.note.id} 的评论"


# 点赞
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='note_likes')
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='note_likes')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='点赞时间')

    class Meta:
        unique_together = ('user', 'note')  # 确保每个用户只能点赞一次
        verbose_name = '日记点赞'
        verbose_name_plural = '日记点赞'

    def __str__(self):
        return f"{self.user.username} 点赞了日记 #{self.note.id}"
