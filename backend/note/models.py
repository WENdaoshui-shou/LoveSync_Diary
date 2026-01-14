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
    is_collaborative = models.BooleanField(default=False, verbose_name='是否为协同日记')
    likes = models.IntegerField(default=0, verbose_name='点赞数')
    comments = models.IntegerField(default=0, verbose_name='评论数')
    
    # 协同编辑相关字段
    collaborators = models.ManyToManyField(User, related_name='collaborative_notes', blank=True, verbose_name='协作者')
    last_editor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='last_edited_notes', verbose_name='最后编辑者')
    last_edit_time = models.DateTimeField(auto_now=True, verbose_name='最后编辑时间')

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


# 协同编辑会话模型
class CollaborativeEditingSession(models.Model):
    """协同编辑会话，用于记录实时编辑状态"""
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='editing_sessions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='editing_sessions')
    is_active = models.BooleanField(default=True, verbose_name='是否活跃')
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name='加入时间')
    last_activity = models.DateTimeField(auto_now=True, verbose_name='最后活动时间')
    cursor_position = models.IntegerField(default=0, verbose_name='光标位置')
    selection_start = models.IntegerField(default=0, verbose_name='选择开始位置')
    selection_end = models.IntegerField(default=0, verbose_name='选择结束位置')

    class Meta:
        unique_together = ('note', 'user')
        verbose_name = '协同编辑会话'
        verbose_name_plural = '协同编辑会话记录'

    def __str__(self):
        return f"{self.user.username} 在编辑日记 #{self.note.id}"


# 编辑操作历史模型
class EditOperation(models.Model):
    """编辑操作历史，用于记录每一次编辑操作"""
    OPERATION_TYPES = [
        ('insert', '插入'),
        ('delete', '删除'),
        ('replace', '替换'),
    ]

    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='edit_operations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='edit_operations')
    operation_type = models.CharField(max_length=10, choices=OPERATION_TYPES, verbose_name='操作类型')
    content = models.TextField(verbose_name='操作内容')
    position = models.IntegerField(verbose_name='操作位置')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')
    revision = models.IntegerField(default=1, verbose_name='版本号')

    class Meta:
        ordering = ['timestamp']
        verbose_name = '编辑操作'
        verbose_name_plural = '编辑操作历史'

    def __str__(self):
        return f"{self.user.username} {self.get_operation_type_display()} 了内容在位置 {self.position}"


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
