from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, CartItemViewSet, mall, product_detail, 
    add_to_cart, cart_count, mallcart, update_cart, 
    mallmark, checkout
)

app_name = 'mall'

# API路由
api_router = DefaultRouter()
api_router.register(r'products', ProductViewSet, basename='product')
api_router.register(r'cart-items', CartItemViewSet, basename='cart-item')

# Web视图路由
web_urlpatterns = [
    path('', mall, name='mall'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('add-to-cart/', add_to_cart, name='add_to_cart'),
    path('cart-count/', cart_count, name='cart_count'),
    path('cart/', mallcart, name='mallcart'),
    path('update-cart/', update_cart, name='update_cart'),
    path('mark/', mallmark, name='mallmark'),
    path('checkout/', checkout, name='checkout'),
    path('checkout/<int:product_id>/', checkout, name='checkout_with_id'),
]

urlpatterns = [
    # API路由
    path('api/', include(api_router.urls)),
    # Web视图路由
    path('', include((web_urlpatterns, 'mall'))),
]