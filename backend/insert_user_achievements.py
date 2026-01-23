import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LoveSync.settings')
django.setup()

from user.models import UserAchievement, Achievement
from django.contrib.auth import get_user_model

User = get_user_model()

# 定义用户ID列表
user_ids = [1, 2]

# 获取所有成就
achievements = Achievement.objects.all()

# 为每个用户创建成就记录
for user_id in user_ids:
    try:
        # 获取用户
        user = User.objects.get(id=user_id)
        print(f"为用户 {user.username} (ID: {user_id}) 创建成就记录...")
        
        # 为每个成就创建用户成就记录
        for achievement in achievements:
            # 检查是否已存在记录
            existing_record = UserAchievement.objects.filter(
                user=user,
                achievement=achievement
            ).first()
            
            if not existing_record:
                # 创建新记录
                user_achievement = UserAchievement.objects.create(
                    user=user,
                    achievement=achievement,
                    unlocked=False,
                    progress=0
                )
                print(f"  - 已创建: {achievement.title}")
            else:
                print(f"  - 已存在: {achievement.title}")
        
        print(f"用户 {user.username} 的成就记录创建完成!\n")
        
    except User.DoesNotExist:
        print(f"用户ID {user_id} 不存在!\n")

print("所有用户的成就记录创建完成!")