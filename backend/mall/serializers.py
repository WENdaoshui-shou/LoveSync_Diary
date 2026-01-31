from rest_framework import serializers
from django.db.models import Sum
from .models import (
    Category, Product, ProductSKU, CartItem, Address, Order, OrderItem,
    Payment, FlashSale, FlashSaleProduct, Coupon, UserCoupon, Logistics,
    ProductMark, HomeBanner, ProductTag, ProductTagRelation, UserBehavior, RefundApplication
)
from core.serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    """商品分类序列化器"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'icon', 'sort', 'is_active', 'created_at']


class ProductTagSerializer(serializers.ModelSerializer):
    """商品标签序列化器"""
    class Meta:
        model = ProductTag
        fields = ['id', 'name', 'color', 'sort', 'is_active']


class ProductSerializer(serializers.ModelSerializer):
    """商品序列化器"""
    category = CategorySerializer(read_only=True)
    tags = serializers.SerializerMethodField()
    skus = serializers.SerializerMethodField()

    def get_tags(self, obj):
        """获取商品标签"""
        return [tag.tag.name for tag in obj.tags.all()]

    def get_skus(self, obj):
        """获取商品规格"""
        return ProductSKUSerializer(obj.skus.filter(is_active=True), many=True).data

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'old_price', 'main_image',
            'detail_image', 'sku_image', 'rating', 'num_reviews', 'category',
            'monthly_sales', 'product_stock', 'is_active', 'is_couple_product',
            'created_at', 'updated_at', 'tags', 'skus'
        ]


class ProductSKUSerializer(serializers.ModelSerializer):
    """商品规格序列化器"""
    product = serializers.SerializerMethodField()

    def get_product(self, obj):
        """获取商品信息"""
        return obj.product.name

    class Meta:
        model = ProductSKU
        fields = ['id', 'product', 'name', 'sku_code', 'price', 'stock', 'image', 'is_active']


class CartItemSerializer(serializers.ModelSerializer):
    """购物车项序列化器"""
    user = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    sku = ProductSKUSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, obj):
        """计算购物车项总价"""
        return obj.total_price

    class Meta:
        model = CartItem
        fields = ['id', 'user', 'product', 'sku', 'quantity', 'selected', 'total_price', 'created_at', 'updated_at']


class CartItemCreateSerializer(serializers.ModelSerializer):
    """创建购物车项序列化器"""
    sku = serializers.PrimaryKeyRelatedField(queryset=ProductSKU.objects.filter(is_active=True), required=False)

    class Meta:
        model = CartItem
        fields = ['product', 'sku', 'quantity', 'selected']

    def create(self, validated_data):
        """创建或更新购物车项"""
        user = self.context['request'].user
        product = validated_data['product']
        sku = validated_data.get('sku')
        quantity = validated_data.get('quantity', 1)
        selected = validated_data.get('selected', True)

        # 检查购物车项是否已存在
        cart_item, created = CartItem.objects.get_or_create(
            user=user,
            product=product,
            sku=sku,
            defaults={'quantity': quantity, 'selected': selected}
        )

        if not created:
            # 如果已存在，更新数量
            cart_item.quantity += quantity
            cart_item.selected = selected
            cart_item.save()

        return cart_item


class AddressSerializer(serializers.ModelSerializer):
    """收货地址序列化器"""
    user = UserSerializer(read_only=True)

    class Meta:
        model = Address
        fields = [
            'id', 'user', 'recipient', 'phone', 'province', 'city', 'district',
            'detail_address', 'postal_code', 'is_default', 'created_at', 'updated_at'
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    """订单项序列化器"""
    product = ProductSerializer(read_only=True)
    sku = ProductSKUSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'sku', 'quantity', 'price', 'total_price']


class OrderSerializer(serializers.ModelSerializer):
    """订单序列化器"""
    user = UserSerializer(read_only=True)
    address = AddressSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    payments = serializers.SerializerMethodField()
    logistics = serializers.SerializerMethodField()

    def get_payments(self, obj):
        """获取支付记录"""
        return PaymentSerializer(obj.payments.all(), many=True).data

    def get_logistics(self, obj):
        """获取物流信息"""
        if hasattr(obj, 'logistics'):
            return LogisticsSerializer(obj.logistics).data
        return None

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'address', 'total_amount', 'status',
            'payment_method', 'shipping_fee', 'logistics_company', 'logistics_no',
            'remark', 'created_at', 'paid_at', 'shipped_at', 'delivered_at',
            'items', 'payments', 'logistics'
        ]


class PaymentSerializer(serializers.ModelSerializer):
    """支付记录序列化器"""
    order = serializers.SerializerMethodField()

    def get_order(self, obj):
        """获取订单信息"""
        return obj.order.order_number

    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'payment_number', 'amount', 'refund_amount', 'method',
            'status', 'transaction_id', 'refund_transaction_id', 'paid_at', 'refunded_at',
            'created_at'
        ]


class FlashSaleProductSerializer(serializers.ModelSerializer):
    """秒杀商品序列化器"""
    product = ProductSerializer(read_only=True)

    class Meta:
        model = FlashSaleProduct
        fields = ['id', 'product', 'flash_price', 'flash_stock', 'limit_per_user']


class FlashSaleSerializer(serializers.ModelSerializer):
    """秒杀活动序列化器"""
    products = FlashSaleProductSerializer(many=True, read_only=True)

    class Meta:
        model = FlashSale
        fields = ['id', 'name', 'start_time', 'end_time', 'status', 'description', 'created_at', 'products']


class CouponSerializer(serializers.ModelSerializer):
    """优惠券序列化器"""
    class Meta:
        model = Coupon
        fields = [
            'id', 'name', 'type', 'value', 'min_spend', 'start_time', 'end_time',
            'total_quantity', 'remaining_quantity', 'is_active', 'created_at'
        ]


class UserCouponSerializer(serializers.ModelSerializer):
    """用户优惠券序列化器"""
    user = UserSerializer(read_only=True)
    coupon = CouponSerializer(read_only=True)
    used_order = serializers.SerializerMethodField()

    def get_used_order(self, obj):
        """获取使用订单信息"""
        if obj.used_order:
            return obj.used_order.order_number
        return None

    class Meta:
        model = UserCoupon
        fields = ['id', 'user', 'coupon', 'is_used', 'used_at', 'used_order', 'obtained_at']


class LogisticsSerializer(serializers.ModelSerializer):
    """物流信息序列化器"""
    order = serializers.SerializerMethodField()

    def get_order(self, obj):
        """获取订单信息"""
        return obj.order.order_number

    class Meta:
        model = Logistics
        fields = [
            'id', 'order', 'logistics_company', 'logistics_no', 'status',
            'latest_status', 'trajectory', 'created_at', 'updated_at'
        ]


class ProductMarkSerializer(serializers.ModelSerializer):
    """商品收藏序列化器"""
    user = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = ProductMark
        fields = ['id', 'user', 'product', 'created_at']


class HomeBannerSerializer(serializers.ModelSerializer):
    """首页轮播图序列化器"""
    class Meta:
        model = HomeBanner
        fields = ['id', 'title', 'image', 'link', 'sort', 'is_active', 'created_at']


class ProductTagRelationSerializer(serializers.ModelSerializer):
    """商品标签关联序列化器"""
    product = ProductSerializer(read_only=True)
    tag = ProductTagSerializer(read_only=True)

    class Meta:
        model = ProductTagRelation
        fields = ['id', 'product', 'tag']


class UserBehaviorSerializer(serializers.ModelSerializer):
    """用户行为序列化器"""
    user = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = UserBehavior
        fields = ['id', 'user', 'product', 'behavior_type', 'created_at']


class RefundApplicationSerializer(serializers.ModelSerializer):
    """退款申请序列化器"""
    user = UserSerializer(read_only=True)
    order = OrderSerializer(read_only=True)
    order_item = OrderItemSerializer(read_only=True)

    class Meta:
        model = RefundApplication
        fields = [
            'id', 'user', 'order', 'order_item', 'refund_amount', 'reason',
            'status', 'remark', 'created_at', 'updated_at'
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    """创建订单序列化器"""
    address = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all())
    items = serializers.ListField(child=serializers.DictField(), write_only=True)

    class Meta:
        model = Order
        fields = ['address', 'items', 'shipping_fee', 'remark']

    def create(self, validated_data):
        """创建订单"""
        user = self.context['request'].user
        address = validated_data['address']
        items_data = validated_data['items']
        shipping_fee = validated_data.get('shipping_fee', 0)
        remark = validated_data.get('remark', '')

        # 计算订单总价
        total_amount = 0
        order_items = []

        for item_data in items_data:
            cart_item = CartItem.objects.get(id=item_data['cart_item_id'])
            price = cart_item.sku.price if cart_item.sku else cart_item.product.price
            item_total = price * cart_item.quantity
            total_amount += item_total

            # 创建订单项
            order_item = OrderItem(
                product=cart_item.product,
                sku=cart_item.sku,
                quantity=cart_item.quantity,
                price=price,
                total_price=item_total
            )
            order_items.append(order_item)

        # 创建订单
        order = Order.objects.create(
            user=user,
            address=address,
            total_amount=total_amount + shipping_fee,
            shipping_fee=shipping_fee,
            remark=remark
        )

        # 保存订单项
        for item in order_items:
            item.order = order
            item.save()

        # 清空购物车中已下单的商品
        CartItem.objects.filter(id__in=[item['cart_item_id'] for item in items_data]).delete()

        return order


class PaymentCreateSerializer(serializers.ModelSerializer):
    """创建支付记录序列化器"""
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.filter(status='pending'))

    class Meta:
        model = Payment
        fields = ['order', 'amount', 'method']

    def create(self, validated_data):
        """创建支付记录"""
        order = validated_data['order']
        amount = validated_data['amount']
        method = validated_data['method']

        # 创建支付记录
        payment = Payment.objects.create(
            order=order,
            amount=amount,
            method=method
        )

        return payment


class CouponApplySerializer(serializers.Serializer):
    """优惠券领取序列化器"""
    coupon_id = serializers.IntegerField()

    def validate_coupon_id(self, value):
        """验证优惠券是否存在且可领取"""
        try:
            coupon = Coupon.objects.get(id=value)
            if not coupon.is_active:
                raise serializers.ValidationError('优惠券已失效')
            if coupon.remaining_quantity <= 0:
                raise serializers.ValidationError('优惠券已领完')
            return value
        except Coupon.DoesNotExist:
            raise serializers.ValidationError('优惠券不存在')


class FlashSalePurchaseSerializer(serializers.Serializer):
    """秒杀购买序列化器"""
    flash_sale_id = serializers.IntegerField()
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, data):
        """验证秒杀活动和商品"""
        flash_sale_id = data['flash_sale_id']
        product_id = data['product_id']
        quantity = data['quantity']

        try:
            flash_sale = FlashSale.objects.get(id=flash_sale_id)
            if not flash_sale.status:
                raise serializers.ValidationError('秒杀活动未开始')

            flash_product = FlashSaleProduct.objects.get(
                flash_sale=flash_sale,
                product_id=product_id
            )
            if flash_product.flash_stock < quantity:
                raise serializers.ValidationError('秒杀库存不足')
            if quantity > flash_product.limit_per_user:
                raise serializers.ValidationError(f'超过每人限购{flash_product.limit_per_user}件')

            # 检查用户是否已达到限购数量
            user = self.context['request'].user
            # 通过订单检查用户购买数量
            from .models import OrderItem
            purchased_count = OrderItem.objects.filter(
                order__user=user,
                order__created_at__gte=flash_sale.start_time,
                order__created_at__lte=flash_sale.end_time,
                product_id=product_id
            ).aggregate(total=Sum('quantity'))['total'] or 0
            
            if purchased_count + quantity > flash_product.limit_per_user:
                raise serializers.ValidationError('超过每人限购数量')

        except FlashSale.DoesNotExist:
            raise serializers.ValidationError('秒杀活动不存在')
        except FlashSaleProduct.DoesNotExist:
            raise serializers.ValidationError('该商品不在秒杀活动中')

        return data
