from rest_framework import serializers
from .models import Cart, CartItem
from .models import Product  # 导入你的商品模型

class CartItemSerializer(serializers.ModelSerializer):
    """购物车项序列化器"""
    product_name = serializers.ReadOnlyField(source='product.name')  # 商品名称
    product_price = serializers.ReadOnlyField(source='product.price')  # 商品单价
    subtotal = serializers.ReadOnlyField()  # 小计（通过模型的@property计算）

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'subtotal']


class CartSerializer(serializers.ModelSerializer):
    """购物车主序列化器"""
    items = CartItemSerializer(many=True, read_only=True)  # 嵌套显示购物车项
    total_price = serializers.ReadOnlyField()  # 总价（通过模型的@property计算）

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'created_at', 'updated_at']