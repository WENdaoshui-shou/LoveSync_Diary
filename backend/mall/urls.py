from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    # API视图集
    CategoryViewSet, ProductViewSet, ProductSKUViewSet, CartItemViewSet, AddressViewSet,
    OrderViewSet, PaymentViewSet, FlashSaleViewSet, CouponViewSet, UserCouponViewSet,
    LogisticsViewSet, ProductMarkViewSet, HomeBannerViewSet, ProductTagViewSet,
    UserBehaviorViewSet, RefundApplicationViewSet,
    # Web视图函数
    mall, product_detail, add_to_cart, cart_count, mark_count, mallcart, update_cart, mallmark, checkout,
    delete_cart_item, submit_order, order_list, order_detail, add_mark, remove_mark, order_review,
    flash_sale, coupon_list, address_manage, add_address, edit_address, delete_address,
    logistics_track, couple_zone, search_result,get_coupon_detail, refresh_recommended, category_products, new_products, vip_products
)

app_name = 'mall'

# API路由
api_router = DefaultRouter()
api_router.register(r'categories', CategoryViewSet, basename='category')
api_router.register(r'products', ProductViewSet, basename='product')
api_router.register(r'product-skus', ProductSKUViewSet, basename='product-sku')
api_router.register(r'cart-items', CartItemViewSet, basename='cart-item')
api_router.register(r'addresses', AddressViewSet, basename='address')
api_router.register(r'orders', OrderViewSet, basename='order')
api_router.register(r'payments', PaymentViewSet, basename='payment')
api_router.register(r'flash-sales', FlashSaleViewSet, basename='flash-sale')
api_router.register(r'coupons', CouponViewSet, basename='coupon')
api_router.register(r'user-coupons', UserCouponViewSet, basename='user-coupon')
api_router.register(r'logistics', LogisticsViewSet, basename='logistics')
api_router.register(r'product-marks', ProductMarkViewSet, basename='product-mark')
api_router.register(r'home-banners', HomeBannerViewSet, basename='home-banner')
api_router.register(r'product-tags', ProductTagViewSet, basename='product-tag')
api_router.register(r'user-behaviors', UserBehaviorViewSet, basename='user-behavior')
api_router.register(r'refund-applications', RefundApplicationViewSet, basename='refund-application')

# Web视图路由
web_urlpatterns = [
    # 首页与商品
    path('', mall, name='mall'),
    path('product/<uuid:product_id>/', product_detail, name='product_detail'),
    path('category/<int:category_id>/', category_products, name='category_products'),
    path('search/', search_result, name='search_result'),
    path('couple-zone/', couple_zone, name='couple_zone'),
    
    # 购物车
    path('add-to-cart/', add_to_cart, name='add_to_cart'),
    path('cart-count/', cart_count, name='cart_count'),
    path('mark-count/', mark_count, name='mark_count'),
    path('cart/', mallcart, name='mallcart'),
    path('update-cart/', update_cart, name='update_cart'),
    path('delete-cart-item/', delete_cart_item, name='delete_cart_item'),
    
    # 订单
    path('checkout/', checkout, name='checkout'),
    path('submit-order/', submit_order, name='submit_order'),
    path('orders/', order_list, name='order_list'),
    path('order/<str:order_number>/', order_detail, name='order_detail'),
    path('order/<int:order_id>/review/', order_review, name='order_review'),
    
    # 收藏
    path('mark/', mallmark, name='mallmark'),
    path('add-mark/', add_mark, name='add_mark'),
    path('remove-mark/', remove_mark, name='remove_mark'),
    
    # 秒杀
    path('flash-sale/', flash_sale, name='flash_sale'),
    
    # 新品
    path('new-products/', new_products, name='new_products'),
    
    # VIP专属
    path('vip/', vip_products, name='vip_products'),
    
    # 优惠券
    path('coupons/', coupon_list, name='coupon_list'),
    
    # 地址管理
    path('addresses/', address_manage, name='address_manage'),
    path('add-address/', add_address, name='add_address'),
    path('edit-address/', edit_address, name='edit_address'),
    path('delete-address/', delete_address, name='delete_address'),
    
    # 优惠券
    path('coupon-detail/<int:coupon_id>/', get_coupon_detail, name='get_coupon_detail'),
    
    # 物流
    path('logistics/<str:order_number>/', logistics_track, name='logistics_track'),
    
    # 推荐商品
    path('api/recommended/refresh/', refresh_recommended, name='refresh_recommended'),
]

urlpatterns = [
    # API路由
    path('api/', include(api_router.urls)),
    # Web视图路由
    path('', include(web_urlpatterns)),
]
