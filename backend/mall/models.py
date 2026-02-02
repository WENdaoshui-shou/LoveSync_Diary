from django.db import models
import uuid
from django.utils import timezone
from core.models import User


class Category(models.Model):
    """商品分类模型"""
    name = models.CharField(max_length=100, verbose_name='分类名称')
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children', 
        verbose_name='父分类'
    )
    icon = models.ImageField(
        upload_to='mall_images/category/', 
        blank=True, 
        null=True, 
        verbose_name='分类图标'
    )
    sort = models.IntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '商品分类'
        verbose_name_plural = '商品分类'
        ordering = ['sort', '-created_at']


def generate_order_number():
    """生成订单编号"""
    return f"ORD{int(timezone.now().timestamp())}{uuid.uuid4().hex[:6].upper()}"


def generate_payment_number():
    """生成支付单号"""
    return f"PAY{int(timezone.now().timestamp())}{uuid.uuid4().hex[:6].upper()}"


class Product(models.Model):
    """商品模型"""
    @staticmethod
    def generate_product_id():
        return str(int(timezone.now().timestamp())) + '-' + str(uuid.uuid4())

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='商品ID')
    name = models.CharField(max_length=200, verbose_name='商品名称')
    description = models.TextField(verbose_name='商品描述', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品价格')
    old_price = models.DecimalField(max_digits=10, decimal_places=2, default=99, verbose_name='商品原价')
    main_image = models.ImageField(
        '商品主图',
        upload_to='mall_images/product/main/%Y%m%d/',
        blank=True
    )
    detail_image = models.ImageField(
        '详情图',
        upload_to='mall_images/product/detail/%Y%m%d/',
        blank=True
    )
    sku_image = models.ImageField(
        'SKU图',
        upload_to='mall_images/product/sku/%Y%m%d/',
        blank=True
    )
    rating = models.FloatField(default=0, verbose_name='商品评分')
    num_reviews = models.IntegerField(default=0, verbose_name='评论数量')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='商品类别')
    monthly_sales = models.IntegerField(default=0, verbose_name='月销量')
    product_stock = models.IntegerField(default=0, verbose_name='库存')
    is_active = models.BooleanField(default=True, verbose_name='是否上架')
    is_couple_product = models.BooleanField(default=False, verbose_name='是否情侣款')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品'
        ordering = ['-created_at']


class ProductSKU(models.Model):
    """商品规格模型"""
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='skus', 
        verbose_name='所属商品'
    )
    name = models.CharField(max_length=200, verbose_name='规格名称')
    sku_code = models.CharField(max_length=50, unique=True, verbose_name='SKU编码')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='规格价格')
    stock = models.IntegerField(default=0, verbose_name='规格库存')
    image = models.ImageField(
        upload_to='mall_images/product/sku/', 
        blank=True, 
        null=True, 
        verbose_name='规格图片'
    )
    is_active = models.BooleanField(default=True, verbose_name='是否启用')

    def __str__(self):
        return f'{self.product.name} - {self.name}'

    class Meta:
        verbose_name = '商品规格'
        verbose_name_plural = '商品规格'


class CartItem(models.Model):
    """购物车项模型"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='cart_items', 
        verbose_name='用户'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='商品')
    sku = models.ForeignKey(
        ProductSKU, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name='商品规格'
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name='数量')
    selected = models.BooleanField(default=False, verbose_name='是否选中')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):  
        return f'{self.user.username} - {self.product.name} x {self.quantity}'

    class Meta:
        unique_together = ('user', 'product', 'sku')
        verbose_name = '购物车项'
        verbose_name_plural = '购物车项'

    @property
    def total_price(self):
        price = self.sku.price if self.sku else self.product.price
        return price * self.quantity


class Address(models.Model):
    """用户收货地址模型"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='addresses', 
        verbose_name='用户'
    )
    recipient = models.CharField(max_length=50, verbose_name='收件人')
    phone = models.CharField(max_length=20, verbose_name='联系电话')
    province = models.CharField(max_length=50, verbose_name='省份')
    city = models.CharField(max_length=50, verbose_name='城市')
    district = models.CharField(max_length=50, verbose_name='区县')
    detail_address = models.CharField(max_length=200, verbose_name='详细地址')
    is_default = models.BooleanField(default=False, verbose_name='是否默认地址')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return f'{self.recipient} - {self.province}{self.city}{self.district}{self.detail_address}'

    class Meta:
        verbose_name = '收货地址'
        verbose_name_plural = '收货地址'
        ordering = ['-is_default', '-updated_at']

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)


class Order(models.Model):
    """订单模型"""
    ORDER_STATUS_CHOICES = (
        ('pending', '待付款'),
        ('paid', '已付款'),
        ('shipped', '已发货'),
        ('delivered', '已收货'),
        ('cancelled', '已取消'),
        ('refunded', '已退款'),
    )
    order_number = models.CharField(
        max_length=50, 
        unique=True, 
        default=generate_order_number, 
        verbose_name='订单编号'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='orders', 
        verbose_name='用户'
    )
    address = models.ForeignKey(
        Address, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name='收货地址'
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='订单总价')
    status = models.CharField(
        max_length=20, 
        choices=ORDER_STATUS_CHOICES, 
        default='pending', 
        verbose_name='订单状态'
    )
    PAYMENT_METHOD_CHOICES = (
        ('wechat', '微信支付'),
        ('alipay', '支付宝'),
        ('card', '银行卡'),
    )
    payment_method = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name='支付方式'
    )
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='运费')
    logistics_company = models.CharField(max_length=100, blank=True, null=True, verbose_name='物流公司')
    logistics_no = models.CharField(max_length=50, blank=True, null=True, verbose_name='物流单号')
    remark = models.TextField(blank=True, null=True, verbose_name='订单备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='付款时间')
    shipped_at = models.DateTimeField(null=True, blank=True, verbose_name='发货时间')
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name='收货时间')

    def __str__(self):
        return self.order_number

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = '订单'
        ordering = ['-created_at']


class OrderItem(models.Model):
    """订单项模型"""
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items', 
        verbose_name='所属订单'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='商品')
    sku = models.ForeignKey(
        ProductSKU, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name='商品规格'
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name='数量')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='购买单价')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='订单项总价')

    def __str__(self):
        return f'{self.order.order_number} - {self.product.name} x {self.quantity}'

    class Meta:
        verbose_name = '订单项'
        verbose_name_plural = '订单项'

    def save(self, *args, **kwargs):
        self.total_price = self.price * self.quantity
        super().save(*args, **kwargs)


class Payment(models.Model):
    """支付记录模型"""
    PAYMENT_STATUS_CHOICES = (
        ('pending', '待支付'),
        ('success', '支付成功'),
        ('failed', '支付失败'),
        ('refunded', '已退款'),
    )
    PAYMENT_METHOD_CHOICES = (
        ('wechat', '微信支付'),
        ('alipay', '支付宝'),
        ('card', '银行卡'),
    )
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='payments', 
        verbose_name='所属订单'
    )
    payment_number = models.CharField(
        max_length=50, 
        unique=True, 
        default=generate_payment_number, 
        verbose_name='支付单号'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='支付金额')
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='退款金额')
    method = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHOD_CHOICES, 
        verbose_name='支付方式'
    )
    status = models.CharField(
        max_length=20, 
        choices=PAYMENT_STATUS_CHOICES, 
        default='pending', 
        verbose_name='支付状态'
    )
    transaction_id = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name='第三方交易号'
    )
    refund_transaction_id = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name='退款交易号'
    )
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='支付时间')
    refunded_at = models.DateTimeField(null=True, blank=True, verbose_name='退款时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return f'{self.payment_number} - {self.amount}元'

    class Meta:
        verbose_name = '支付记录'
        verbose_name_plural = '支付记录'
        ordering = ['-created_at']


class FlashSale(models.Model):
    """秒杀活动模型"""
    name = models.CharField(max_length=100, verbose_name='活动名称')
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    status = models.BooleanField(default=False, verbose_name='活动状态')
    description = models.TextField(blank=True, null=True, verbose_name='活动描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '秒杀活动'
        verbose_name_plural = '秒杀活动'
        ordering = ['-start_time']


class FlashSaleProduct(models.Model):
    """秒杀商品模型"""
    flash_sale = models.ForeignKey(FlashSale, on_delete=models.CASCADE, related_name='products', verbose_name='秒杀活动')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='flash_sales', verbose_name='商品')
    flash_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='秒杀价格')
    flash_stock = models.IntegerField(default=0, verbose_name='秒杀库存')
    limit_per_user = models.IntegerField(default=1, verbose_name='每人限购数量')

    def __str__(self):
        return f'{self.flash_sale.name} - {self.product.name}'

    class Meta:
        verbose_name = '秒杀商品'
        verbose_name_plural = '秒杀商品'
        unique_together = ('flash_sale', 'product')


class Coupon(models.Model):
    """优惠券模型"""
    COUPON_TYPE_CHOICES = (
        ('满减券', '满减券'),
        ('折扣券', '折扣券'),
        ('现金券', '现金券'),
    )
    name = models.CharField(max_length=100, verbose_name='优惠券名称')
    type = models.CharField(max_length=20, choices=COUPON_TYPE_CHOICES, verbose_name='优惠券类型')
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='优惠券价值')
    min_spend = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='最低消费')
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    total_quantity = models.IntegerField(default=0, verbose_name='总数量')
    remaining_quantity = models.IntegerField(default=0, verbose_name='剩余数量')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '优惠券'
        verbose_name_plural = '优惠券'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.remaining_quantity = self.total_quantity
        super().save(*args, **kwargs)


class UserCoupon(models.Model):
    """用户优惠券模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coupons', verbose_name='用户')
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='user_coupons', verbose_name='优惠券')
    is_used = models.BooleanField(default=False, verbose_name='是否使用')
    used_at = models.DateTimeField(null=True, blank=True, verbose_name='使用时间')
    used_order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='used_coupons', verbose_name='使用订单')
    obtained_at = models.DateTimeField(auto_now_add=True, verbose_name='获取时间')

    def __str__(self):
        return f'{self.user.username} - {self.coupon.name}'

    class Meta:
        verbose_name = '用户优惠券'
        verbose_name_plural = '用户优惠券'
        ordering = ['-obtained_at']


class Logistics(models.Model):
    """物流信息模型"""
    LOGISTICS_STATUS_CHOICES = (
        ('pending', '待发货'),
        ('shipped', '已发货'),
        ('in_transit', '运输中'),
        ('delivered', '已送达'),
        ('exception', '异常'),
    )
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='logistics', verbose_name='订单')
    logistics_company = models.CharField(max_length=100, verbose_name='物流公司')
    logistics_no = models.CharField(max_length=50, verbose_name='物流单号')
    status = models.CharField(max_length=20, choices=LOGISTICS_STATUS_CHOICES, default='pending', verbose_name='物流状态')
    latest_status = models.CharField(max_length=200, blank=True, null=True, verbose_name='最新状态描述')
    trajectory = models.TextField(blank=True, null=True, verbose_name='物流轨迹')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return f'{self.order.order_number} - {self.logistics_no}'

    class Meta:
        verbose_name = '物流信息'
        verbose_name_plural = '物流信息'


class ProductMark(models.Model):
    """商品收藏模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_marks', verbose_name='用户')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='marks', verbose_name='商品')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')

    def __str__(self):
        return f'{self.user.username} - {self.product.name}'

    class Meta:
        verbose_name = '商品收藏'
        verbose_name_plural = '商品收藏'
        unique_together = ('user', 'product')
        ordering = ['-created_at']


class HomeBanner(models.Model):
    """首页轮播图模型"""
    title = models.CharField(max_length=100, verbose_name='轮播图标题')
    image = models.ImageField(upload_to='mall_images/banner/%Y%m%d/', verbose_name='轮播图图片')
    link = models.CharField(max_length=200, blank=True, null=True, verbose_name='跳转链接')
    sort = models.IntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '首页轮播图'
        verbose_name_plural = '首页轮播图'
        ordering = ['sort', '-created_at']


class ProductTag(models.Model):
    """商品标签模型"""
    name = models.CharField(max_length=50, verbose_name='标签名称')
    color = models.CharField(max_length=20, default='#333333', verbose_name='标签颜色')
    sort = models.IntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '商品标签'
        verbose_name_plural = '商品标签'
        ordering = ['sort']


class ProductTagRelation(models.Model):
    """商品标签关联模型"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='tags', verbose_name='商品')
    tag = models.ForeignKey(ProductTag, on_delete=models.CASCADE, related_name='products', verbose_name='标签')

    def __str__(self):
        return f'{self.product.name} - {self.tag.name}'

    class Meta:
        verbose_name = '商品标签关联'
        verbose_name_plural = '商品标签关联'
        unique_together = ('product', 'tag')


class UserBehavior(models.Model):
    """用户行为记录模型"""
    BEHAVIOR_TYPE_CHOICES = (
        ('view', '浏览'),
        ('add_cart', '加入购物车'),
        ('mark', '收藏'),
        ('purchase', '购买'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='behaviors', verbose_name='用户')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='behaviors', verbose_name='商品')
    behavior_type = models.CharField(max_length=20, choices=BEHAVIOR_TYPE_CHOICES, verbose_name='行为类型')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='行为时间')

    def __str__(self):
        return f'{self.user.username} - {self.get_behavior_type_display()} - {self.product.name}'

    class Meta:
        verbose_name = '用户行为'
        verbose_name_plural = '用户行为'
        ordering = ['-created_at']


class ProductReview(models.Model):
    """商品评论模型"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reviews', 
        verbose_name='用户'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='reviews', 
        verbose_name='商品'
    )
    order_item = models.ForeignKey(
        OrderItem, 
        on_delete=models.CASCADE, 
        related_name='review', 
        verbose_name='订单项'
    )
    rating = models.PositiveIntegerField(
        choices=[(1, '1星'), (2, '2星'), (3, '3星'), (4, '4星'), (5, '5星')], 
        verbose_name='评分'
    )
    comment = models.TextField(verbose_name='评论内容')
    images = models.ImageField(
        upload_to='mall_images/product/review_images/', 
        max_length=500, 
        blank=True, 
        null=True, 
        verbose_name='评论图片'
    )
    is_anonymous = models.BooleanField(
        default=False, 
        verbose_name='是否匿名'
    )
    is_approved = models.BooleanField(
        default=True, 
        verbose_name='是否审核通过'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name='更新时间'
    )

    def __str__(self):
        return f'{self.user.username} 对 {self.product.name} 的评价'

    class Meta:
        verbose_name = '商品评论'
        verbose_name_plural = '商品评论'
        ordering = ['-created_at']


class RefundApplication(models.Model):
    """退款申请模型"""
    REFUND_STATUS_CHOICES = (
        ('pending', '待审核'),
        ('approved', '审核通过'),
        ('rejected', '审核拒绝'),
        ('refunded', '已退款'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refunds', verbose_name='用户')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='refunds', verbose_name='订单')
    order_item = models.ForeignKey(OrderItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='refunds', verbose_name='订单项')
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='退款金额')
    reason = models.TextField(verbose_name='退款原因')
    status = models.CharField(max_length=20, choices=REFUND_STATUS_CHOICES, default='pending', verbose_name='退款状态')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='申请时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return f'{self.user.username} - {self.order.order_number}'

    class Meta:
        verbose_name = '退款申请'
        verbose_name_plural = '退款申请'
        ordering = ['-created_at']
