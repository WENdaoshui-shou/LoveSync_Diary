from django.db import models
import uuid
from django.utils import timezone
from core.models import User


class Product(models.Model):

    def generate_product_id():
        return str(int(timezone.now().timestamp())) + '-' + str(uuid.uuid4())

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='商品ID')
    name = models.CharField(max_length=200, verbose_name='商品名称')
    description = models.TextField(verbose_name='商品描述', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品价格')
    old_price = models.DecimalField(max_digits=10, decimal_places=2, default=99, verbose_name='商品原价')
    image = models.ImageField(
        upload_to="products/id/",  # 使用自定义路径函数
        blank=True,
        null=True,
        verbose_name='商品图片'
    )
    rating = models.FloatField(default=0, verbose_name='商品评分')
    num_reviews = models.IntegerField(default=0, verbose_name='评论数量')
    category = models.CharField(max_length=100, verbose_name='商品类别')
    monthly_sales = models.IntegerField(default=0, verbose_name='月销量')
    product_stock = models.IntegerField(default=0, verbose_name='库存')

    def __str__(self):
        return self.name


class CartItem(models.Model):
    """购物车数据持久化模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product')  # 同一用户的同一商品唯一