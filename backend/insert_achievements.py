import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LoveSync.settings')
django.setup()

from user.models import Achievement

# 定义成就数据
achievements_data = [
    {
        'title': '初次相遇',
        'description': '成功邀请伴侣加入LoveSync',
        'icon': '💕',
        'requirement': '邀请伴侣注册并完成情侣绑定',
        'category': '基础'
    },
    {
        'title': '甜蜜开始',
        'description': '完成第一次情侣测试',
        'icon': '🧪',
        'requirement': '完成任意一次情侣测试',
        'category': '互动'
    },
    {
        'title': '爱的足迹',
        'description': '添加第一个情侣景点',
        'icon': '🗺️',
        'requirement': '添加第一个情侣共同去过的地方',
        'category': '记录'
    },
    {
        'title': '记录美好',
        'description': '发布第一条动态',
        'icon': '📝',
        'requirement': '发布第一条情侣动态',
        'category': '分享'
    },
    {
        'title': '爱的相册',
        'description': '上传第一张照片到相册',
        'icon': '📸',
        'requirement': '上传第一张照片到情侣相册',
        'category': '分享'
    },
    {
        'title': '游戏达人',
        'description': '完成第一个情侣游戏',
        'icon': '🎮',
        'requirement': '完成任意一个情侣游戏',
        'category': '互动'
    },
    {
        'title': '纪念时刻',
        'description': '添加第一个纪念日',
        'icon': '🎉',
        'requirement': '添加第一个情侣纪念日',
        'category': '记录'
    },
    {
        'title': '每日打卡',
        'description': '连续7天登录',
        'icon': '📅',
        'requirement': '连续7天登录LoveSync',
        'category': '坚持'
    },
    {
        'title': '一周年纪念',
        'description': '庆祝情侣关系一周年',
        'icon': '🎂',
        'requirement': '情侣关系满一周年',
        'category': '纪念'
    },
    {
        'title': '社交达人',
        'description': '关注10个其他情侣',
        'icon': '👥',
        'requirement': '关注10个其他情侣用户',
        'category': '社交'
    }
]

# 插入成就数据
for achievement_data in achievements_data:
    # 检查是否已存在相同标题的成就
    existing_achievement = Achievement.objects.filter(
        title=achievement_data['title']
    ).first()
    
    if not existing_achievement:
        Achievement.objects.create(**achievement_data)
        print(f"已插入成就: {achievement_data['title']} (分类: {achievement_data['category']})")
    else:
        print(f"成就已存在: {achievement_data['title']} (分类: {achievement_data['category']})")

print("\n成就数据插入完成!")