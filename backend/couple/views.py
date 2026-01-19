from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView
from django.db import models
from .models import Anniversary, CoupleTask, TaskCompletion
from .serializers import AnniversarySerializer, CoupleTaskSerializer, TaskCompletionSerializer


class AnniversaryViewSet(viewsets.ModelViewSet):
    """纪念日视图集"""
    queryset = Anniversary.objects.all()
    serializer_class = AnniversarySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的纪念日"""
        return self.queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """创建纪念日时自动关联当前用户"""
        serializer.save(user=self.request.user)


class CoupleTaskViewSet(viewsets.ModelViewSet):
    """情侣任务视图集"""
    queryset = CoupleTask.objects.all()
    serializer_class = CoupleTaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的情侣任务"""
        return self.queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """创建情侣任务时自动关联当前用户"""
        serializer.save(user=self.request.user)


class TaskCompletionViewSet(viewsets.ModelViewSet):
    """任务完成记录视图集"""
    queryset = TaskCompletion.objects.all()
    serializer_class = TaskCompletionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的任务完成记录"""
        return self.queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """创建任务完成记录时自动关联当前用户"""
        serializer.save(user=self.request.user)


# 情侣首页视图
@login_required
def couple_view(request):
    """情侣首页视图"""
    from core.models import Profile
    import logging
    
    # 设置日志记录器
    logger = logging.getLogger('django')
    
    from django.contrib import messages
    
    # 调用get_messages()获取消息，但会保存并重新添加
    all_messages = list(messages.get_messages(request))

    # 将消息重新添加回请求中，确保模板能显示
    for message in all_messages:
        messages.add_message(request, message.level, message.message, extra_tags=message.tags)
    
    # 获取当前用户的个人资料
    profile = request.user.profile
    
    # 获取当前用户发送的请求（当前用户发送给他人的请求）
    sent_request = profile.couple_pending
    
    # 获取当前用户收到的请求（他人发送给当前用户的请求）
    # 使用try-except处理OneToOneField反向关系可能的异常
    try:
        received_request = profile.pending_partner
    except:
        received_request = None
    
    # 检查是否已有情侣
    has_couple = profile.couple is not None
    
    context = {
        'profile': profile,
        'sent_request': sent_request,  # 当前用户发送的请求
        'received_request': received_request,  # 当前用户收到的请求
        'has_couple': has_couple
    }
    
    return render(request, 'couple.html', context)


# 邀请伴侣视图
@login_required
def invite_partner_view(request):
    """邀请伴侣视图"""
    from core.models import Profile
    from django.contrib import messages
    
    if request.method == 'POST':
        couple_code = request.POST.get('couple_code', '').strip()
        
        if couple_code:
            try:
                # 查找拥有该邀请码的用户
                target_profile = Profile.objects.get(couple_code=couple_code)
                
                # 检查是否是自己
                if target_profile == request.user.profile:
                    messages.error(request, '不能向自己发送情侣请求')
                else:
                    # 发送情侣请求
                    request.user.profile.send_couple_request(target_profile)
                    messages.success(request, '情侣请求已发送，请等待对方回应')
            except Profile.DoesNotExist:
                messages.error(request, '邀请码无效，请检查后重新输入')
            except Exception as e:
                messages.error(request, f'发送请求失败: {str(e)}')
        else:
            messages.error(request, '请输入邀请码')
    
    return redirect('couple_web:couple')


# 爱情故事视图
@login_required
def love_story_view(request):
    """爱情故事视图"""
    from core.models import LoveStoryTimeline
    
    # 检查用户是否绑定情侣
    if not request.user.profile.couple:
        messages.error(request, '请先绑定情侣关系，才能使用爱情故事功能！')
        return redirect('couple_web:couple')
    
    # 获取当前用户的爱情故事时间轴
    timeline_events = LoveStoryTimeline.objects.filter(user=request.user).order_by('-date')
    
    # 获取伴侣的爱情故事时间轴
    partner_timeline_events = []
    if request.user.profile.couple:
        partner = request.user.profile.couple.user
        partner_timeline_events = LoveStoryTimeline.objects.filter(user=partner).order_by('-date')
    
    # 合并并按日期排序
    all_events = list(timeline_events) + list(partner_timeline_events)
    all_events.sort(key=lambda x: x.date, reverse=True)
    
    context = {
        'timeline_events': timeline_events,
        'partner_timeline_events': partner_timeline_events,
        'all_events': all_events
    }
    
    return render(request, 'couple.html', context)


# 情侣测试视图
@login_required
def couple_test_view(request):
    """情侣测试视图"""
    from core.models import Profile, CoupleQuiz
    
    # 检查用户是否绑定情侣
    if not request.user.profile.couple:
        messages.error(request, '请先绑定情侣关系，才能使用情侣测试功能！')
        return redirect('couple_web:couple')
    
    # 获取情侣测试问题
    quizzes = CoupleQuiz.objects.filter(user=request.user)
    
    # 获取伴侣的测试问题
    partner_quizzes = []
    if request.user.profile.couple:
        partner = request.user.profile.couple.user
        partner_quizzes = CoupleQuiz.objects.filter(user=partner)
    
    context = {
        'quizzes': quizzes,
        'partner_quizzes': partner_quizzes
    }
    
    return render(request, 'couple_test.html', context)


# 情侣景点视图
@login_required
def couple_places_view(request):
    """情侣景点视图"""
    from core.models import Profile, CouplePlace
    
    # 检查用户是否绑定情侣
    if not request.user.profile.couple:
        messages.error(request, '请先绑定情侣关系，才能使用情侣景点功能！')
        return redirect('couple_web:couple')
    
    # 从数据库获取情侣地点数据
    try:
        # 获取所有情侣地点，按评分和评价数量排序
        places = CouplePlace.objects.all().order_by('-rating', '-review_count')
        
        # 构建地点数据列表
        places_data = []
        for place in places:
            place_dict = {
                'id': place.id,
                                    'name': place.name,
                                    'description': place.description,
                                    'address': place.address,
                                    'place_type': place.get_place_type_display(),
                                    'rating': place.rating,
                                    'review_count': place.review_count,
                                    'price_range': place.price_range,
                                'image_url': place.image_url,
            }
            places_data.append(place_dict)
    except Exception as e:
        print(f"Error fetching couple places: {e}")
        places_data = []
    
    context = {
        'places': places_data,
        'has_dynamic_content': len(places_data) > 0
    }
    
    return render(request, 'couple_places.html', context)


# 情侣地点分页API
@login_required
def couple_places_api(request):
    """情侣地点分页API"""
    from core.models import CouplePlace
    from django.http import JsonResponse
    
    try:
        # 获取分页参数
        page = int(request.GET.get('page', 1))
        page_size = 10  # 每页10条数据
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 获取情侣地点，按评分和评价数量排序
        places = CouplePlace.objects.all().order_by('-rating', '-review_count')[offset:offset + page_size]
        
        # 构建地点数据列表
        places_data = []
        for place in places:
            place_dict = {
                'id': place.id,
                'name': place.name,
                'description': place.description,
                'address': place.address,
                'place_type': place.get_place_type_display(),
                'rating': place.rating,
                'review_count': place.review_count,
                'price_range': place.price_range,
                'image_url': place.image_url
            }
            places_data.append(place_dict)
        
        # 检查是否还有更多数据
        has_more = CouplePlace.objects.all().count() > offset + page_size
        
        return JsonResponse({
            'success': True,
            'places': places_data,
            'has_more': has_more,
            'page': page
        })
    
    except Exception as e:
        print(f"Error in couple_places_api: {e}")
        return JsonResponse({
            'success': False,
            'message': f'获取地点失败: {str(e)}'
        }, status=500)


# 情侣推荐视图
@login_required
def couple_recommendation_view(request):
    """情侣推荐视图"""
    from core.models import Profile
    
    # 检查用户是否绑定情侣
    if not request.user.profile.couple:
        messages.error(request, '请先绑定情侣关系，才能使用情侣推荐功能！')
        return redirect('couple_web:couple')
    
    # 模拟获取情侣活动推荐
    # 实际项目中，这里应该基于用户兴趣和历史行为推荐
    recommendations = [
        {
            'id': 1,
            'title': '情侣烹饪课程',
            'description': '一起学习制作浪漫晚餐',
            'category': '活动',
            'price': '¥299/对',
            'rating': 4.9,
            'image': 'https://picsum.photos/seed/cooking/400/300'
        },
        {
            'id': 2,
            'title': '情侣瑜伽',
            'description': '增进感情的同时锻炼身体',
            'category': '健康',
            'price': '¥199/对',
            'rating': 4.7,
            'image': 'https://picsum.photos/seed/yoga/400/300'
        },
        {
            'id': 3,
            'title': '情侣摄影套餐',
            'description': '记录你们的美好时光',
            'category': '摄影',
            'price': '¥599/套',
            'rating': 4.8,
            'image': 'https://picsum.photos/seed/photo/400/300'
        },
        {
            'id': 4,
            'title': '情侣旅行攻略',
            'description': '为你们的下一次旅行做准备',
            'category': '旅行',
            'price': '免费',
            'rating': 4.6,
            'image': 'https://picsum.photos/seed/travel/400/300'
        }
    ]
    
    context = {
        'recommendations': recommendations
    }
    
    return render(request, 'couple_recommendation.html', context)


# 情侣历史视图
@login_required
def couple_history_view(request):
    """情侣历史视图"""
    from core.models import CoupleRelationHistory
    from django.utils import timezone
    
    # 获取当前用户的所有情侣关系历史记录
    # 包括作为user1和user2的记录
    user = request.user
    relation_history = CoupleRelationHistory.objects.filter(
        models.Q(user1=user) | models.Q(user2=user)
    ).order_by('-ended_at')
    
    # 准备历史记录数据，添加伴侣信息和关系时长
    history_data = []
    
    # 首先检查当前是否有正在进行的情侣关系
    profile = request.user.profile
    if profile.couple and profile.couple_joined_at:
        # 当前有情侣关系，添加到历史记录中
        partner = profile.couple.user
        started_at = profile.couple_joined_at
        ended_at = timezone.now()
        
        # 计算关系时长
        duration = ended_at - started_at
        duration_days = duration.days
        duration_months = duration_days // 30
        duration_years = duration_days // 365
        
        # 格式化关系时长
        if duration_years > 0:
            duration_str = f"{duration_years}年{duration_months % 12}个月"
        elif duration_months > 0:
            duration_str = f"{duration_months}个月{duration_days % 30}天"
        else:
            duration_str = f"{duration_days}天"
        
        history_data.append({
            'partner': partner,
            'started_at': started_at.strftime('%Y-%m-%d'),
            'ended_at': '至今',
            'duration': duration_str,
            'duration_days': duration_days,
            'record_id': None,
            'is_current': True
        })
    
    # 然后添加历史记录
    for record in relation_history:
        # 确定伴侣是谁
        if record.user1 == user:
            partner = record.user2
        else:
            partner = record.user1
        
        # 计算关系时长
        duration = record.ended_at - record.started_at
        duration_days = duration.days
        duration_months = duration_days // 30
        duration_years = duration_days // 365
        
        # 格式化关系时长
        if duration_years > 0:
            duration_str = f"{duration_years}年{duration_months % 12}个月"
        elif duration_months > 0:
            duration_str = f"{duration_months}个月{duration_days % 30}天"
        else:
            duration_str = f"{duration_days}天"
        
        history_data.append({
            'partner': partner,
            'started_at': record.started_at.strftime('%Y-%m-%d'),
            'ended_at': record.ended_at.strftime('%Y-%m-%d'),
            'duration': duration_str,
            'duration_days': duration_days,
            'record_id': record.id,
            'is_current': False
        })
    
    context = {
        'history_data': history_data
    }
    
    return render(request, 'couple_history.html', context)


# 删除情侣关系历史记录
@login_required
def delete_couple_history(request, history_id):
    """删除情侣关系历史记录"""
    from core.models import CoupleRelationHistory
    from django.http import JsonResponse
    
    try:
        # 获取历史记录
        history = CoupleRelationHistory.objects.get(id=history_id)
        
        # 检查当前用户是否是记录的参与者
        if request.user != history.user1 and request.user != history.user2:
            return JsonResponse({'success': False, 'message': '你没有权限删除这条记录'}, status=403)
        
        # 删除记录
        history.delete()
        
        return JsonResponse({'success': True, 'message': '记录已成功删除'})
    except CoupleRelationHistory.DoesNotExist:
        return JsonResponse({'success': False, 'message': '记录不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'删除失败: {str(e)}'}, status=500)


# 接受情侣请求视图
@login_required
def accept_request(request):
    """接受情侣请求"""
    from core.models import Profile
    
    try:
        # 获取当前用户的个人资料
        profile = request.user.profile
        # 调用模型方法接受请求
        profile.accept_couple_request()
        messages.success(request, '已成功接受情侣请求')
    except Exception as e:
        messages.error(request, f'接受请求失败: {str(e)}')
    
    return redirect('couple_web:couple')


# 拒绝情侣请求视图
@login_required
def reject_request(request):
    """拒绝情侣请求"""
    from core.models import Profile
    
    try:
        # 获取当前用户的个人资料
        profile = request.user.profile
        # 调用模型方法拒绝请求
        profile.reject_couple_request()
        messages.success(request, '已成功拒绝情侣请求')
    except Exception as e:
        messages.error(request, f'拒绝请求失败: {str(e)}')
    
    return redirect('couple_web:couple')


# 取消情侣请求视图
@login_required
def cancel_request(request):
    """取消情侣请求"""
    from core.models import Profile
    
    try:
        # 获取当前用户的个人资料
        profile = request.user.profile
        # 调用模型方法取消请求
        if profile.couple_pending:
            # 清除待处理请求
            requester = profile
            recipient = profile.couple_pending
            
            requester.couple_pending = None
            
            # 如果收件人也有对应的待处理请求，也需要清除
            if recipient.couple_pending == requester:
                recipient.couple_pending = None
                recipient.save()
            
            requester.save()
            messages.success(request, '已成功取消情侣请求')
        else:
            messages.error(request, '没有待取消的情侣请求')
    except Exception as e:
        messages.error(request, f'取消请求失败: {str(e)}')
    
    return redirect('couple_web:couple')


# 解除情侣关系视图
@login_required
def breakup(request):
    """解除情侣关系"""
    from core.models import Profile
    
    try:
        # 获取当前用户的个人资料
        profile = request.user.profile
        # 调用模型方法解除情侣关系
        if profile.couple:
            profile.break_up()
            messages.success(request, '已成功解除情侣关系')
        else:
            messages.error(request, '你没有情侣关系')
    except Exception as e:
        messages.error(request, f'解除情侣关系失败: {str(e)}')
    
    return redirect('couple_web:couple')


# 情侣设置视图
@login_required
def couple_settings(request):
    """保存情侣设置"""
    from core.models import Profile
    
    if request.method == 'POST':
        try:
            # 获取当前用户的个人资料
            profile = request.user.profile
            
            # 保存基本信息
            my_nickname = request.POST.get('my_nickname')
            if my_nickname:
                profile.user.name = my_nickname
                profile.user.save()
            
            # 保存恋爱纪念日
            anniversary = request.POST.get('anniversary')
            if anniversary:
                from django.utils import timezone
                from datetime import datetime
                anniversary_date = datetime.strptime(anniversary, '%Y-%m-%d').date()
                # 转换为datetime对象
                anniversary_datetime = datetime.combine(anniversary_date, datetime.min.time())
                profile.couple_joined_at = timezone.make_aware(anniversary_datetime)
            
            # 保存其他设置
            # 这里可以根据需要添加更多设置的保存逻辑
            
            profile.save()
            messages.success(request, '设置已保存')
        except Exception as e:
            messages.error(request, f'保存设置失败: {str(e)}')
    
    return redirect('couple_web:couple')