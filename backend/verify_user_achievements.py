import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LoveSync.settings')
django.setup()

from user.models import UserAchievement
from django.contrib.auth import get_user_model

User = get_user_model()

# 定义用户ID列表
user_ids = [1, 2]

# 验证每个用户的成就记录
for user_id in user_ids:
    try:
        # 获取用户
        user = User.objects.get(id=user_id)
        print(f"用户 {user.username} (ID: {user_id}) 的成就记录:")
        
        # 获取用户的所有成就记录
        user_achievements = UserAchievement.objects.filter(user=user)
        print(f"  成就记录数量: {user_achievements.count()}")
        
        # 打印每个成就记录
        for ua in user_achievements:
            print(f"  - {ua.achievement.title}: 解锁状态={ua.unlocked}, 进度={ua.progress}%")
        
        print()
        
    except User.DoesNotExist:
        print(f"用户ID {user_id} 不存在!\n")

print("验证完成!")