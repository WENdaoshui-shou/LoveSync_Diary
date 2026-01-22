from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AnniversaryViewSet, CoupleTaskViewSet, TaskCompletionViewSet,
    couple_view, invite_partner_view, 
    love_story_view, couple_test_view, couple_places_view, 
    couple_recommendation_view, couple_history_view, delete_couple_history,
    accept_request, reject_request, cancel_request, breakup, couple_settings,
    couple_places_api, couple_test_api, submit_test_result
)

app_name = 'couple'

# API路由
api_router = DefaultRouter()
api_router.register(r'anniversaries', AnniversaryViewSet, basename='anniversary')
api_router.register(r'tasks', CoupleTaskViewSet, basename='couple_task')
api_router.register(r'task-completions', TaskCompletionViewSet, basename='task_completion')

# Web视图路由
web_urlpatterns = [
    path('', couple_view, name='couple'),
    path('invite/', invite_partner_view, name='invite_partner'),
    path('accept/', accept_request, name='accept_request'),
    path('reject/', reject_request, name='reject_request'),
    path('cancel/', cancel_request, name='cancel_request'),
    path('breakup/', breakup, name='breakup'),
    path('settings/', couple_settings, name='couple_settings'),
    path('love-story/', love_story_view, name='love_story'),
    path('test/', couple_test_view, name='couple_test'),
    path('test/api/', couple_test_api, name='couple_test_api'),
    path('test/submit/', submit_test_result, name='submit_test_result'),
    path('places/', couple_places_view, name='couple_places'),
    path('places/api/', couple_places_api, name='couple_places_api'),
    path('recommendation/', couple_recommendation_view, name='couple_recommendation'),
    path('history/', couple_history_view, name='couple_history'),
    path('history/delete/<int:history_id>/', delete_couple_history, name='delete_couple_history'),
]

urlpatterns = [
    # API路由
    path('api/', include(api_router.urls)),
    # Web视图路由
    *web_urlpatterns,
]