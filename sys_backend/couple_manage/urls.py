from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RecommendedCouplesViewSet,
    PlaceManagementViewSet,
    LoveTestManagementViewSet,
    CoupleGameManagementViewSet
)

router = DefaultRouter()
router.register(r'recommended-couples', RecommendedCouplesViewSet, basename='recommended-couple')
router.register(r'places', PlaceManagementViewSet, basename='place')
router.register(r'love-tests', LoveTestManagementViewSet, basename='love-test')
router.register(r'couple-games', CoupleGameManagementViewSet, basename='couple-game')

urlpatterns = [
    path('', include(router.urls)),
]