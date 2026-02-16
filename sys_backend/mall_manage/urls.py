from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductManagementViewSet,
    CategoryManagementViewSet,
    OrderManagementViewSet,
    PaymentManagementViewSet,
    FlashSaleManagementViewSet,
    CouponManagementViewSet,
    BannerManagementViewSet,
    AddressManagementViewSet
)

# 创建路由器
router = DefaultRouter()

# 注册视图集
router.register(r'products', ProductManagementViewSet, basename='product')
router.register(r'categories', CategoryManagementViewSet, basename='category')
router.register(r'orders', OrderManagementViewSet, basename='order')
router.register(r'payments', PaymentManagementViewSet, basename='payment')
router.register(r'flash-sales', FlashSaleManagementViewSet, basename='flash-sale')
router.register(r'coupons', CouponManagementViewSet, basename='coupon')
router.register(r'banners', BannerManagementViewSet, basename='banner')
router.register(r'addresses', AddressManagementViewSet, basename='address')

# 定义URL模式
urlpatterns = [
    path('', include(router.urls)),
]
