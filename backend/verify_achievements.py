import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LoveSync.settings')
django.setup()

from user.models import Achievement

# 打印成就数量
print('成就数量:', Achievement.objects.count())

# 打印所有成就
print('\n成就列表:')
for a in Achievement.objects.all():
    print(f'{a.title} - {a.category} - {a.icon}')
    print(f'  描述: {a.description}')
    print(f'  要求: {a.requirement}')
    print()