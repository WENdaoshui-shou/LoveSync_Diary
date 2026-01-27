from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommunityEventViewSet

app_name = 'sys_community'

router = DefaultRouter()
router.register(r'events', CommunityEventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
]
