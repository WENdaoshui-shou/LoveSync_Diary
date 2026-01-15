from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.models import VIPMember, VIPOrder

User = get_user_model()

class VIPFunctionTests(TestCase):
    """VIP功能测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        
        # 创建VIPMember记录
        self.vip = VIPMember.objects.create(user=self.user)
    
    def test_vip_index_view(self):
        """测试VIP首页视图"""
        response = self.client.get(reverse('vip:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '会员信息')
    
    def test_vip_benefits_view(self):
        """测试VIP权益视图"""
        response = self.client.get(reverse('vip:benefits'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '会员权益')
    
    def test_recharge_records_view(self):
        """测试充值记录视图"""
        response = self.client.get(reverse('vip:recharge_records'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '充值记录')
    
    def test_create_recharge_view(self):
        """测试创建充值视图"""
        response = self.client.get(reverse('vip:create_recharge'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '开通/续费会员')
    
    def test_recharge_functionality(self):
        """测试充值功能"""
        # 测试充值10元
        response = self.client.post(reverse('vip:create_recharge'), {
            'amount': 10
        })
        self.assertEqual(response.status_code, 302)  # 重定向
        
        # 验证VIP状态更新
        self.vip.refresh_from_db()
        self.assertTrue(self.vip.is_active)
        self.assertEqual(self.vip.total_recharge, 10.00)
        
        # 验证订单创建
        orders = VIPOrder.objects.filter(user=self.user)
        self.assertEqual(orders.count(), 1)
        
    def test_vip_level_upgrade(self):
        """测试VIP等级自动升级"""
        # 初始等级应为normal
        self.assertEqual(self.vip.level, 'normal')
        
        # 充值50元，应升级到bronze
        self.client.post(reverse('vip:create_recharge'), {'amount': 50})
        self.vip.refresh_from_db()
        self.assertEqual(self.vip.level, 'bronze')
        
        # 再充值50元，累计100元，应升级到silver
        self.client.post(reverse('vip:create_recharge'), {'amount': 50})
        self.vip.refresh_from_db()
        self.assertEqual(self.vip.level, 'silver')
    
    def test_vip_status_check(self):
        """测试VIP状态检查"""
        # 充值10元，激活VIP
        self.client.post(reverse('vip:create_recharge'), {'amount': 10})
        self.vip.refresh_from_db()
        self.assertTrue(self.vip.is_active)
        
        # 手动将VIP设置为过期
        from django.utils import timezone
        self.vip.end_date = timezone.now() - timezone.timedelta(days=1)
        self.vip.save()
        
        # 访问任意页面，触发中间件检查
        self.client.get(reverse('vip:index'))
        
        # 验证VIP状态已更新
        self.vip.refresh_from_db()
        self.assertFalse(self.vip.is_active)
