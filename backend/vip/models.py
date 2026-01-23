from django.db import models
from django.conf import settings

# VIP会员模型
class VIPMember(models.Model):
    """VIP会员模型"""
    VIP_LEVELS = [
        ('normal', 'Ⅰ'),
        ('bronze', 'Ⅱ'),
        ('silver', 'Ⅲ'),
        ('diamond', 'Ⅳ'),
        ('king', 'Ⅴ'),
        ('god', 'Ⅵ'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vip')
    level = models.CharField(max_length=20, choices=VIP_LEVELS, default='normal', verbose_name='VIP等级')
    start_date = models.DateTimeField(auto_now_add=True, verbose_name='开通时间')
    end_date = models.DateTimeField(null=True, blank=True, verbose_name='到期时间')
    is_active = models.BooleanField(default=False, verbose_name='是否活跃')
    renewal_count = models.IntegerField(default=0, verbose_name='续费次数')
    total_recharge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='累计充值金额')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = 'VIP会员'
        verbose_name_plural = 'VIP会员管理'
        ordering = ['-level']
    
    def __str__(self):
        return f'{self.user.username} - {self.get_level_display()}'
    
    def get_level_color(self):
        """获取VIP等级对应的颜色"""
        color_map = {
                'normal': 'linear-gradient(135deg, #F3F4F6, #E5E7EB)', 
                'bronze': 'linear-gradient(135deg, #8B4513, #FFD700)',  
                'silver': 'linear-gradient(135deg, #C0C0C0, #333333)', 
                'diamond': 'linear-gradient(135deg, #00BFFF, #006400)',
                'king': 'linear-gradient(135deg, #FF6347, #FFB6C1)',
                'god': 'linear-gradient(135deg, #722ED1, #FF6B8B)'
                }
        return color_map.get(self.level, 'linear-gradient(135deg, #F3F4F6, #E5E7EB)')
    
    def get_level_text_color(self):
        """获取VIP等级对应的文字颜色"""
        text_color_map = {
            'bronze': '#fff',
            'silver': '#fff',
            'diamond': '#fff',
            'king': '#fff',
            'god': '#fff',
        }
        return text_color_map.get(self.level, '#666')
    
    def activate_vip(self, duration_days=30):
        """激活VIP会员"""
        from django.utils import timezone
        now = timezone.now()
        self.start_date = now
        self.end_date = now + timezone.timedelta(days=duration_days)
        self.is_active = True
        self.renewal_count += 1
        self.save()
        return True
    
    def renew_vip(self, duration_days=30):
        """续费VIP会员"""
        from django.utils import timezone
        now = timezone.now()
        if self.end_date and self.end_date > now:
            # 如果VIP还在有效期内，从到期时间开始续费
            self.end_date += timezone.timedelta(days=duration_days)
        else:
            # 如果VIP已经过期，从现在开始续费
            self.start_date = now
            self.end_date = now + timezone.timedelta(days=duration_days)
        self.is_active = True
        self.renewal_count += 1
        self.save()
        return True
    
    def check_vip_status(self):
        """检查VIP状态并处理到期情况"""
        from django.utils import timezone
        now = timezone.now()
        if self.end_date and self.end_date < now:
            self.is_active = False
            # VIP到期后，保持等级不变，但标记为非活跃状态
            self.save()
        return self.is_active
    
    def update_vip_level(self):
        """根据累计充值金额更新VIP等级"""
        total = self.total_recharge
        new_level = 'normal'
        
        # 根据累计充值金额确定VIP等级
        if total >= 10000:
            new_level = 'god'  
        elif total >= 5000:
            new_level = 'king'  
        elif total >= 648:
            new_level = 'diamond'  
        elif total >= 128:
            new_level = 'silver'
        elif total >= 6:
            new_level = 'bronze'
        
        # 如果等级发生变化，更新等级
        if self.level != new_level:
            self.level = new_level
            self.save()
        
        return new_level

# VIP特权模型
class VIPPrivilege(models.Model):
    """VIP特权模型"""
    name = models.CharField(max_length=100, verbose_name='特权名称')
    description = models.TextField(verbose_name='特权描述')
    required_level = models.CharField(max_length=20, choices=VIPMember.VIP_LEVELS, verbose_name='所需VIP等级')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = 'VIP特权'
        verbose_name_plural = 'VIP特权管理'
        ordering = ['-required_level']
    
    def __str__(self):
        return f'{self.name} - {self.get_required_level_display()}'


# VIP充值订单模型
class VIPOrder(models.Model):
    """VIP充值订单模型"""
    STATUS_CHOICES = [
        ('pending', '待支付'),
        ('success', '支付成功'),
        ('failed', '支付失败'),
        ('cancelled', '已取消'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vip_orders', verbose_name='用户')
    amount = models.IntegerField(verbose_name='充值金额')
    duration = models.IntegerField(verbose_name='充值时长(天)')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='订单状态')
    order_number = models.CharField(max_length=50, unique=True, verbose_name='订单号')
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='支付时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = 'VIP充值订单'
        verbose_name_plural = 'VIP充值订单管理'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'订单 {self.order_number} - {self.get_status_display()}'