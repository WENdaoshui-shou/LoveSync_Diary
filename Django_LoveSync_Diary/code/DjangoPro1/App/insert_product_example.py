import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoPro1.settings')
import django
django.setup()
from App.models import Product
import uuid


def insert_product():
    # 创建一个新的商品实例
    for product_data in [
    {
        "name": "智能手表 Pro",
        "description": "具有心率监测、睡眠分析和GPS功能的高级智能手表",
        "price": "199.99",
        "image": "https://picsum.photos/id/1/300/300",
        "rating": 4.8,
        "num_reviews": 245,
        "category": "电子产品",
        "monthly_sales": 1234
    },
    {
        "name": "无线蓝牙耳机",
        "description": "主动降噪、防水设计的高品质无线耳机",
        "price": "129.99",
        "image": "https://picsum.photos/id/2/300/300",
        "rating": 4.6,
        "num_reviews": 189,
        "category": "电子产品",
        "monthly_sales": 987
    },
    {
        "name": "机械键盘 RGB",
        "description": "全尺寸机械键盘，RGB背光，Cherry MX轴体",
        "price": "89.99",
        "image": "https://picsum.photos/id/3/300/300",
        "rating": 4.7,
        "num_reviews": 320,
        "category": "电脑配件",
        "monthly_sales": 765
    },
    {
        "name": "4K高清显示器",
        "description": "27英寸4K分辨率，HDR支持，IPS面板",
        "price": "349.99",
        "image": "https://picsum.photos/id/4/300/300",
        "rating": 4.9,
        "num_reviews": 156,
        "category": "电脑配件",
        "monthly_sales": 543
    },
    {
        "name": "游戏鼠标",
        "description": "16000 DPI，可编程按键，轻量化设计",
        "price": "59.99",
        "image": "https://picsum.photos/id/5/300/300",
        "rating": 4.5,
        "num_reviews": 210,
        "category": "电脑配件",
        "monthly_sales": 678
    },
    {
        "name": "超薄笔记本电脑",
        "description": "14英寸轻薄本，Intel酷睿i7，16GB内存",
        "price": "899.99",
        "image": "https://picsum.photos/id/6/300/300",
        "rating": 4.8,
        "num_reviews": 178,
        "category": "电子产品",
        "monthly_sales": 432
    },
    {
        "name": "便携式充电宝",
        "description": "20000mAh大容量，双向快充，数显电量",
        "price": "49.99",
        "image": "https://picsum.photos/id/7/300/300",
        "rating": 4.4,
        "num_reviews": 342,
        "category": "电子产品",
        "monthly_sales": 987
    },
    {
        "name": "智能恒温保温杯",
        "description": "不锈钢真空内胆，智能温度显示，长效保温",
        "price": "39.99",
        "image": "https://picsum.photos/id/8/300/300",
        "rating": 4.6,
        "num_reviews": 129,
        "category": "生活用品",
        "monthly_sales": 321
    },
    {
        "name": "无线充电器",
        "description": "15W快充，多设备兼容，铝合金外壳",
        "price": "29.99",
        "image": "https://picsum.photos/id/9/300/300",
        "rating": 4.3,
        "num_reviews": 215,
        "category": "电子产品",
        "monthly_sales": 567
    },
    {
        "name": "电动牙刷",
        "description": "声波震动，5种清洁模式，2分钟定时",
        "price": "79.99",
        "image": "https://picsum.photos/id/10/300/300",
        "rating": 4.7,
        "num_reviews": 192,
        "category": "生活用品",
        "monthly_sales": 654
    },
    {
        "name": "空气净化器",
        "description": "CADR值500，3重过滤，智能APP控制",
        "price": "249.99",
        "image": "https://picsum.photos/id/11/300/300",
        "rating": 4.8,
        "num_reviews": 145,
        "category": "家用电器",
        "monthly_sales": 234
    },
    {
        "name": "便携式投影仪",
        "description": "1080p支持，5小时续航，自动对焦",
        "price": "399.99",
        "image": "https://picsum.photos/id/12/300/300",
        "rating": 4.6,
        "num_reviews": 112,
        "category": "家用电器",
        "monthly_sales": 123
    },
    {
        "name": "机械硬盘 2TB",
        "description": "7200RPM，SATA3接口，NAS兼容",
        "price": "79.99",
        "image": "https://picsum.photos/id/13/300/300",
        "rating": 4.5,
        "num_reviews": 230,
        "category": "电脑配件",
        "monthly_sales": 456
    },
    {
        "name": "蓝牙音箱",
        "description": "360°环绕音效，IPX7防水，24小时续航",
        "price": "89.99",
        "image": "https://picsum.photos/id/14/300/300",
        "rating": 4.7,
        "num_reviews": 167,
        "category": "电子产品",
        "monthly_sales": 345
    },
    {
        "name": "游戏手柄",
        "description": "无线连接，振动反馈，可充电电池",
        "price": "59.99",
        "image": "https://picsum.photos/id/15/300/300",
        "rating": 4.4,
        "num_reviews": 201,
        "category": "电脑配件",
        "monthly_sales": 567
    },
    {
        "name": "智能门锁",
        "description": "指纹识别，密码，APP远程控制，自动锁门",
        "price": "199.99",
        "image": "https://picsum.photos/id/16/300/300",
        "rating": 4.9,
        "num_reviews": 134,
        "category": "智能家居",
        "monthly_sales": 234
    },
    {
        "name": "运动手环",
        "description": "心率监测，睡眠分析，运动模式，防水",
        "price": "39.99",
        "image": "https://picsum.photos/id/17/300/300",
        "rating": 4.3,
        "num_reviews": 278,
        "category": "电子产品",
        "monthly_sales": 678
    },
    {
        "name": "高清摄像头",
        "description": "1080p@60fps，自动对焦，广角镜头",
        "price": "49.99",
        "image": "https://picsum.photos/id/18/300/300",
        "rating": 4.6,
        "num_reviews": 156,
        "category": "电脑配件",
        "monthly_sales": 345
    },
    {
        "name": "USB-C扩展坞",
        "description": "8合1接口，支持4K视频输出，千兆网口",
        "price": "69.99",
        "image": "https://picsum.photos/id/19/300/300",
        "rating": 4.8,
        "num_reviews": 123,
        "category": "电脑配件",
        "monthly_sales": 234
    },
    {
        "name": "智能插座",
        "description": "WiFi控制，定时开关，电量统计",
        "price": "19.99",
        "image": "https://picsum.photos/id/20/300/300",
        "rating": 4.5,
        "num_reviews": 189,
        "category": "智能家居",
        "monthly_sales": 456
    }
]:
        new_product = Product(**product_data)
        new_product.save()
    print("商品插入成功！")


if __name__ == "__main__":
    insert_product()