from moment.models import Moment
from django.utils import timezone

# 检查最近7天的动态
start_date = timezone.now() - timezone.timedelta(days=7)
print('最近7天动态数:', Moment.objects.filter(created_at__gte=start_date).count())
print('最近7天动态详情:')
for m in Moment.objects.filter(created_at__gte=start_date):
    print(f'ID: {m.id}, 创建时间: {m.created_at}, 点赞: {m.likes}, 评论: {m.comments}, 收藏: {m.favorites}, 浏览: {m.view_count}, is_shared: {m.is_shared}')

# 检查所有动态
print('\n所有动态数:', Moment.objects.count())
print('所有动态详情:')
for m in Moment.objects.all():
    print(f'ID: {m.id}, 创建时间: {m.created_at}, 点赞: {m.likes}, 评论: {m.comments}, 收藏: {m.favorites}, 浏览: {m.view_count}, is_shared: {m.is_shared}')
