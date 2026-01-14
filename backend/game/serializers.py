from rest_framework import serializers
from .models import (
    Game, GameQuestion, GameSession, GameAnswer, 
    GameScore, Achievement, UserAchievement, GameLeaderboard
)


class GameSerializer(serializers.ModelSerializer):
    """游戏主模型序列化器"""
    class Meta:
        model = Game
        fields = ['id', 'name', 'description', 'game_type', 'difficulty', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class GameQuestionSerializer(serializers.ModelSerializer):
    """游戏问题模型序列化器"""
    class Meta:
        model = GameQuestion
        fields = ['id', 'game', 'question', 'options', 'correct_answer', 'score_value', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class GameSessionSerializer(serializers.ModelSerializer):
    """游戏会话模型序列化器"""
    class Meta:
        model = GameSession
        fields = ['id', 'user', 'game', 'partner', 'score', 'is_completed', 'started_at', 'completed_at', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class GameAnswerSerializer(serializers.ModelSerializer):
    """游戏答案模型序列化器"""
    class Meta:
        model = GameAnswer
        fields = ['id', 'session', 'question', 'user', 'answer', 'is_correct', 'score', 'created_at']
        read_only_fields = ['created_at']


class GameScoreSerializer(serializers.ModelSerializer):
    """游戏得分模型序列化器"""
    class Meta:
        model = GameScore
        fields = ['id', 'user', 'game', 'high_score', 'total_score', 'play_count', 'win_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class AchievementSerializer(serializers.ModelSerializer):
    """成就勋章模型序列化器"""
    class Meta:
        model = Achievement
        fields = ['id', 'name', 'description', 'icon', 'requirement', 'points', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class UserAchievementSerializer(serializers.ModelSerializer):
    """用户成就模型序列化器"""
    class Meta:
        model = UserAchievement
        fields = ['id', 'user', 'achievement', 'is_unlocked', 'unlocked_at', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class GameLeaderboardSerializer(serializers.ModelSerializer):
    """游戏排行榜模型序列化器"""
    class Meta:
        model = GameLeaderboard
        fields = ['id', 'game', 'user', 'score', 'rank', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class GameSessionDetailSerializer(serializers.ModelSerializer):
    """游戏会话详情序列化器"""
    answers = GameAnswerSerializer(many=True, read_only=True)
    game = GameSerializer(read_only=True)
    
    class Meta:
        model = GameSession
        fields = ['id', 'user', 'game', 'partner', 'score', 'is_completed', 'started_at', 'completed_at', 'answers']
        read_only_fields = ['answers', 'game', 'started_at', 'completed_at']