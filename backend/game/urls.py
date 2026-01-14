from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GameViewSet, GameQuestionViewSet, GameSessionViewSet, GameAnswerViewSet,
    GameScoreViewSet, AchievementViewSet, UserAchievementViewSet, GameLeaderboardViewSet,
    game_list_view, game_detail_view, game_leaderboard_view, achievements_view
)

app_name = 'game'

# API路由
api_router = DefaultRouter()
api_router.register(r'games', GameViewSet, basename='game')
api_router.register(r'questions', GameQuestionViewSet, basename='game_question')
api_router.register(r'sessions', GameSessionViewSet, basename='game_session')
api_router.register(r'answers', GameAnswerViewSet, basename='game_answer')
api_router.register(r'scores', GameScoreViewSet, basename='game_score')
api_router.register(r'achievements', AchievementViewSet, basename='achievement')
api_router.register(r'user-achievements', UserAchievementViewSet, basename='user_achievement')
api_router.register(r'leaderboards', GameLeaderboardViewSet, basename='game_leaderboard')

# Web视图路由
web_urlpatterns = [
    path('list/', game_list_view, name='game_list'),
    path('detail/<int:game_id>/', game_detail_view, name='game_detail'),
    path('leaderboard/<int:game_id>/', game_leaderboard_view, name='game_leaderboard'),
    path('achievements/', achievements_view, name='achievements'),
]

urlpatterns = [
    # API路由
    path('api/', include(api_router.urls)),
    # Web视图路由
    path('', include(web_urlpatterns)),
]