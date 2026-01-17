from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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
    from core.models import Profile
    
    # 检查用户是否绑定情侣
    if not request.user.profile.couple:
        messages.error(request, '请先绑定情侣关系，才能使用情侣游戏功能！')
        return redirect('couple_web:couple')
    
    # 从数据库获取所有激活状态的游戏
    games = Game.objects.filter(is_active=True)
    
    # 获取游戏统计信息
    total_games = games.count()
    total_sessions = GameSession.objects.filter(user=request.user, is_completed=True).count()
    total_score = sum(session.score for session in GameSession.objects.filter(user=request.user, is_completed=True))
    
    # 获取用户最近玩过的游戏
    recent_sessions = GameSession.objects.filter(user=request.user, is_completed=True).order_by('-completed_at')[:5]
    
    # 获取用户游戏成就
    user_achievements = UserAchievement.objects.filter(user=request.user, is_unlocked=True).order_by('-unlocked_at')[:5]
    
    # 获取热门游戏排行榜
    popular_games = []
    for game in games:
        game_sessions = GameSession.objects.filter(game=game, is_completed=True).count()
        if game_sessions > 0:
            avg_score = sum(session.score for session in GameSession.objects.filter(game=game, is_completed=True)) / game_sessions
            popular_games.append({
                'game': game,
                'sessions': game_sessions,
                'avg_score': round(avg_score, 1)
            })
    popular_games.sort(key=lambda x: x['sessions'], reverse=True)
    popular_games = popular_games[:5]
    
    # 获取推荐游戏（基于用户游戏历史）
    recommended_games = []
    if recent_sessions:
        # 基于用户最近玩过的游戏类型推荐
        recent_game_types = set(session.game.game_type for session in recent_sessions)
        for game in games:
            if game.game_type in recent_game_types and game not in [session.game for session in recent_sessions]:
                recommended_games.append(game)
        # 如果推荐游戏不足3个，添加其他游戏
        if len(recommended_games) < 3:
            for game in games:
                if game not in recommended_games and game not in [session.game for session in recent_sessions]:
                    recommended_games.append(game)
                    if len(recommended_games) == 3:
                        break
    
    context = {
        'games': games,
        'total_games': total_games,
        'total_sessions': total_sessions,
        'total_score': total_score,
        'recent_sessions': recent_sessions,
        'user_achievements': user_achievements,
        'popular_games': popular_games,
        'recommended_games': recommended_games,
        'has_dynamic_content': True
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
    # 重定向到core应用的成就页面
    return redirect('/core/achievements/')