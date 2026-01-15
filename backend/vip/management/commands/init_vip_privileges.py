from django.core.management.base import BaseCommand
from core.models import VIPPrivilege, VIPMember

class Command(BaseCommand):
    help = '初始化VIP特权数据'

    def handle(self, *args, **kwargs):
        # 定义默认的VIP特权数据
        privileges_data = [
            {
                'name': '专属标识',
                'description': '在个人主页显示专属VIP标识，彰显尊贵身份',
                'required_level': 'bronze'
            },
            {
                'name': '优先体验',
                'description': '优先体验平台新功能，提前享受专属服务',
                'required_level': 'bronze'
            },
            {
                'name': '专属福利',
                'description': '定期获得专属福利，包括虚拟道具、优惠券等',
                'required_level': 'silver'
            },
            {
                'name': '高清图片上传',
                'description': '上传高清图片，不受压缩限制，保留美好瞬间',
                'required_level': 'silver'
            },
            {
                'name': '无广告体验',
                'description': '去除平台所有广告，享受纯净浏览体验',
                'required_level': 'gold'
            },
            {
                'name': '专属客服',
                'description': '享受24小时专属客服服务，优先解决问题',
                'required_level': 'gold'
            },
            {
                'name': '个性化定制',
                'description': '根据个人喜好定制平台内容，享受专属推荐',
                'required_level': 'platinum'
            },
            {
                'name': '专属活动',
                'description': '参加平台举办的专属活动，获得更多奖励',
                'required_level': 'platinum'
            },
            {
                'name': '钻石专属标识',
                'description': '显示独特的钻石VIP标识，彰显最高尊贵身份',
                'required_level': 'diamond'
            },
            {
                'name': '专属特权日',
                'description': '每月固定日期享受专属特权，包括双倍积分、专属折扣等',
                'required_level': 'diamond'
            }
        ]

        # 插入数据
        created_count = 0
        for privilege_data in privileges_data:
            # 检查是否已存在
            privilege, created = VIPPrivilege.objects.get_or_create(
                name=privilege_data['name'],
                defaults=privilege_data
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'成功初始化 {created_count} 条VIP特权数据'))
        self.stdout.write(self.style.SUCCESS(f'当前共有 {VIPPrivilege.objects.count()} 条VIP特权数据'))
