from django.core.management.base import BaseCommand
from core.models import CouplePlace
import random

class Command(BaseCommand):
    """生成情侣地点测试数据"""
    help = 'Generate test data for couple places'

    def handle(self, *args, **kwargs):
        # 定义地点类型和示例数据
        place_types = ['restaurant', 'cafe', 'park', 'movie', 'museum', 'activity', 'other']
        place_names = [
            '浪漫咖啡馆', '情侣主题公园', '爱情博物馆', '星空电影院', '云端餐厅',
            '薰衣草庄园', '艺术画廊', '海边栈道', '温泉度假村', '山顶观景台',
            '水族馆', '植物园', '音乐厅', '滑雪场', '露营基地'
        ]
        descriptions = [
            '环境优雅，适合情侣约会',
            '有专门的情侣活动区域',
            '展示爱情故事和纪念品',
            '情侣专属包厢，环境浪漫',
            '位于城市最高建筑顶层，提供法式料理和城市全景',
            '大片的薰衣草田，四季都有不同的花卉盛开',
            '集现代艺术展览、互动体验和创意工坊于一体',
            '沿着海岸线建造的浪漫栈道',
            '提供情侣温泉套房和SPA服务',
            '俯瞰城市全景的浪漫地点',
            '海底世界的奇妙之旅',
            '热带植物的天堂',
            '浪漫的音乐演出',
            '冬季的浪漫运动',
            '亲近自然的浪漫体验'
        ]
        addresses = [
            '北京市朝阳区建国路88号',
            '北京市海淀区颐和园路19号',
            '北京市东城区王府井大街99号',
            '北京市西城区西单北大街120号',
            '北京市朝阳区三里屯SOHO',
            '北京市怀柔区薰衣草庄园路',
            '北京市朝阳区798艺术区',
            '北京市海淀区昆玉河畔',
            '北京市昌平区温泉镇',
            '北京市海淀区香山公园',
            '北京市海淀区中关村南大街',
            '北京市海淀区北京植物园',
            '北京市西城区复兴门内大街',
            '北京市延庆区滑雪场',
            '北京市密云区露营基地'
        ]
        price_ranges = ['¥50以下', '¥50-100', '¥100-200', '¥200-300', '¥300以上']

        # 生成15个情侣地点
        for i in range(15):
            place = CouplePlace(
                name=random.choice(place_names),
                description=random.choice(descriptions),
                address=random.choice(addresses),
                place_type=random.choice(place_types),
                rating=round(random.uniform(3.5, 5.0), 1),
                review_count=random.randint(10, 200),
                price_range=random.choice(price_ranges),
                latitude=39.9042 + random.uniform(-0.1, 0.1),  # 北京附近的纬度
                longitude=116.4074 + random.uniform(-0.1, 0.1),  # 北京附近的经度
                image_url=f'https://picsum.photos/600/300?random={i+1}'
            )
            place.save()
            self.stdout.write(self.style.SUCCESS(f'Created couple place: {place.name}'))

        self.stdout.write(self.style.SUCCESS('Successfully generated 15 couple places'))