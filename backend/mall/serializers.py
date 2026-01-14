from rest_framework import serializers
from .models import Product, CartItem
from core.serializers import UserSerializer


class ProductSerializer(serializers.ModelSerializer):
    """商品序列化器"""
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'old_price', 'image', 'rating', 'num_reviews', 'category', 'monthly_sales', 'product_stock']


class CartItemSerializer(serializers.ModelSerializer):
    """购物车商品序列化器"""
    user = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'user', 'product', 'quantity', 'created_at', 'updated_at']


class CartItemCreateSerializer(serializers.ModelSerializer):
    """创建购物车商品序列化器"""
    class Meta:
        model = CartItem
        fields = ['product', 'quantity']
    
    def create(self, validated_data):
        """创建或更新购物车商品"""
        user = self.context['request'].user
        product = validated_data['product']
        quantity = validated_data['quantity']
        
        # 检查商品是否已存在于购物车中
        cart_item, created = CartItem.objects.get_or_create(
            user=user,
            product=product,
            defaults={'quantity': quantity}
        )
        
        # 如果商品已存在，则更新数量
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return cart_item