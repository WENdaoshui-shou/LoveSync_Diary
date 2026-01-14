from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import (
    Game, GameQuestion, GameSession, GameAnswer, 
    GameScore, Achievement, UserAchievement, GameLeaderboard
)
from .serializers import (
    GameSerializer, GameQuestionSerializer, GameSessionSerializer, GameAnswerSerializer,
    GameScoreSerializer, AchievementSerializer, UserAchievementSerializer, GameLeaderboardSerializer,
    GameSessionDetailSerializer
)


class GameViewSet(viewsets.ModelViewSet):
    """游戏主视图集"""
    queryset = Game.objects.filter(is_active=True)
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取激活状态的游戏"""
        return self.queryset


class GameQuestionViewSet(viewsets.ModelViewSet):
    """游戏问题视图集"""
    queryset = GameQuestion.objects.all()
    serializer_class = GameQuestionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """根据游戏ID过滤问题"""
        queryset = self.queryset
        game_id = self.request.query_params.get('game_id')
        if game_id:
            queryset = queryset.filter(game_id=game_id)
        return queryset


class GameSessionViewSet(viewsets.ModelViewSet):
    """游戏会话视图集"""
    queryset = GameSession.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """根据请求方法选择序列化器"""
        if self.action == 'retrieve':
            return GameSessionDetailSerializer
        return GameSessionSerializer
    
    def get_queryset(self):
        """获取当前用户的游戏会话"""
        return self.queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """创建游戏会话时自动关联当前用户"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """完成游戏会话"""
        session = self.get_object()
        final_score = request.data.get('score', 0)
        session.complete_session(final_score)
        
        # 更新游戏得分
        game_score, created = GameScore.objects.get_or_create(user=request.user, game=session.game)
        game_score.update_score(final_score)
        
        # 更新排行榜
        leaderboard, created = GameLeaderboard.objects.get_or_create(game=session.game, user=request.user)
        if final_score > leaderboard.score:
            leaderboard.score = final_score
            leaderboard.save()
            leaderboard.update_rank()
        
        return Response({'status': '游戏会话已完成', 'final_score': final_score})


class GameAnswerViewSet(viewsets.ModelViewSet):
    """游戏答案视图集"""
    queryset = GameAnswer.objects.all()
    serializer_class = GameAnswerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的游戏答案"""
        return self.queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """创建游戏答案时自动关联当前用户"""
        serializer.save(user=self.request.user)


class GameScoreViewSet(viewsets.ModelViewSet):
    """游戏得分视图集"""
    queryset = GameScore.objects.all()
    serializer_class = GameScoreSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的游戏得分"""
        return self.queryset.filter(user=self.request.user)


class AchievementViewSet(viewsets.ModelViewSet):
    """成就勋章视图集"""
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取所有成就"""
        return self.queryset


class UserAchievementViewSet(viewsets.ModelViewSet):
    """用户成就视图集"""
    queryset = UserAchievement.objects.all()
    serializer_class = UserAchievementSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的成就"""
        return self.queryset.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def unlock(self, request, pk=None):
        """解锁成就"""
        user_achievement = self.get_object()
        user_achievement.unlock()
        return Response({'status': '成就已解锁'})


class GameLeaderboardViewSet(viewsets.ModelViewSet):
    """游戏排行榜视图集"""
    queryset = GameLeaderboard.objects.all()
    serializer_class = GameLeaderboardSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """根据游戏ID过滤排行榜"""
        queryset = self.queryset
        game_id = self.request.query_params.get('game_id')
        if game_id:
            queryset = queryset.filter(game_id=game_id).order_by('rank')
        return queryset


# Web视图
@login_required
def game_list_view(request):
    """游戏列表视图"""
    # 从数据库获取所有激活状态的游戏
    games = Game.objects.filter(is_active=True)
    
    context = {
        'games': games
    }
    return render(request, 'game_list.html', context)


@login_required
def game_detail_view(request, game_id):
    """游戏详情视图"""
    return render(request, 'game_detail.html', {'game_id': game_id})


@login_required
def game_leaderboard_view(request, game_id):
    """游戏排行榜视图"""
    return render(request, 'game_leaderboard.html', {'game_id': game_id})


@login_required
def achievements_view(request):
    """成就列表视图"""
    return render(request, 'achievements.html')