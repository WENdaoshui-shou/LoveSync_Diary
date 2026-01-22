from django.db import models
from core.models import User
from django.utils import timezone


# 游戏类型选择
GAME_TYPE_CHOICES = [
    ('task', '任务'),
    ('challenge', '挑战'),
    ('adventure', '冒险'),
]

# 游戏难度选择
GAME_DIFFICULTY_CHOICES = [
    ('easy', '简单'),
    ('medium', '中等'),
    ('hard', '困难'),
]


class Game(models.Model):
    """游戏主模型"""
    name = models.CharField(max_length=100, verbose_name='游戏名称')
    description = models.TextField(verbose_name='游戏描述')
    game_type = models.CharField(max_length=20, choices=GAME_TYPE_CHOICES, verbose_name='游戏类型')
    difficulty = models.CharField(max_length=20, choices=GAME_DIFFICULTY_CHOICES, default='easy', verbose_name='游戏难度')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '游戏'
        verbose_name_plural = '游戏管理'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.name} ({self.get_game_type_display()})'


class GameQuestion(models.Model):
    """游戏问题模型"""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='questions', verbose_name='所属游戏')
    question = models.TextField(verbose_name='问题内容')
    options = models.JSONField(verbose_name='选项列表', default=list)
    correct_answer = models.CharField(max_length=100, verbose_name='正确答案')
    score_value = models.IntegerField(default=10, verbose_name='分值')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '游戏问题'
        verbose_name_plural = '游戏问题管理'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.game.name} - {self.question[:50]}'


class GameSession(models.Model):
    """游戏会话模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_sessions', verbose_name='用户')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='sessions', verbose_name='游戏')
    partner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='partner_game_sessions', verbose_name='伴侣')
    score = models.IntegerField(default=0, verbose_name='得分')
    is_completed = models.BooleanField(default=False, verbose_name='是否完成')
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='开始时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '游戏会话'
        verbose_name_plural = '游戏会话管理'
        ordering = ['-started_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.game.name} - {self.started_at}'
    
    def complete_session(self, final_score):
        """完成游戏会话"""
        self.score = final_score
        self.is_completed = True
        self.completed_at = timezone.now()
        self.save()
        return True


class GameAnswer(models.Model):
    """游戏答案模型"""
    session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='answers', verbose_name='游戏会话')
    question = models.ForeignKey(GameQuestion, on_delete=models.CASCADE, related_name='answers', verbose_name='问题')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_answers', verbose_name='用户')
    answer = models.CharField(max_length=100, verbose_name='用户答案')
    is_correct = models.BooleanField(default=False, verbose_name='是否正确')
    score = models.IntegerField(default=0, verbose_name='得分')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '游戏答案'
        verbose_name_plural = '游戏答案管理'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.question.question[:50]}'


class GameScore(models.Model):
    """游戏得分模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_scores', verbose_name='用户')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='scores', verbose_name='游戏')
    high_score = models.IntegerField(default=0, verbose_name='最高分')
    total_score = models.IntegerField(default=0, verbose_name='总得分')
    play_count = models.IntegerField(default=0, verbose_name='游戏次数')
    win_count = models.IntegerField(default=0, verbose_name='获胜次数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '游戏得分'
        verbose_name_plural = '游戏得分管理'
        unique_together = ('user', 'game')
        ordering = ['-high_score']
    
    def __str__(self):
        return f'{self.user.username} - {self.game.name} - 最高分: {self.high_score}'
    
    def update_score(self, new_score):
        """更新游戏得分"""
        self.total_score += new_score
        if new_score > self.high_score:
            self.high_score = new_score
        self.play_count += 1
        self.save()
        return True


class Achievement(models.Model):
    """成就勋章模型"""
    name = models.CharField(max_length=100, verbose_name='成就名称')
    description = models.TextField(verbose_name='成就描述')
    icon = models.ImageField(upload_to='achievement_icons/', null=True, blank=True, verbose_name='成就图标')
    requirement = models.JSONField(verbose_name='成就要求', default=dict)
    points = models.IntegerField(default=0, verbose_name='成就点数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '成就勋章'
        verbose_name_plural = '成就勋章管理'
        ordering = ['-points']
    
    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    """用户成就模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements', verbose_name='用户')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='user_achievements', verbose_name='成就')
    is_unlocked = models.BooleanField(default=False, verbose_name='是否解锁')
    unlocked_at = models.DateTimeField(null=True, blank=True, verbose_name='解锁时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户成就'
        verbose_name_plural = '用户成就管理'
        unique_together = ('user', 'achievement')
        ordering = ['-unlocked_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.achievement.name}'
    
    def unlock(self):
        """解锁成就"""
        self.is_unlocked = True
        self.unlocked_at = timezone.now()
        self.save()
        return True


class GameLeaderboard(models.Model):
    """游戏排行榜模型"""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='leaderboards', verbose_name='游戏')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaderboard_entries', verbose_name='用户')
    score = models.IntegerField(default=0, verbose_name='得分')
    rank = models.IntegerField(default=0, verbose_name='排名')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '游戏排行榜'
        verbose_name_plural = '游戏排行榜管理'
        unique_together = ('game', 'user')
        ordering = ['rank']
    
    def __str__(self):
        return f'{self.game.name} - {self.user.username} - 排名: {self.rank}'
    
    def update_rank(self):
        """更新排名"""
        # 获取同游戏的所有排行榜条目
        entries = GameLeaderboard.objects.filter(game=self.game).order_by('-score')
        # 更新排名
        for index, entry in enumerate(entries, 1):
            entry.rank = index
            entry.save()
        return True