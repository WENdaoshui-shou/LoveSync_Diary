from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView
from django.db import models
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from .models import Anniversary, CoupleTask, TaskCompletion, QuizQuestion, UserQuizAnswer
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
    from couple.models import CoupleRelation
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
    
    # 获取CoupleRelation数据
    couple_relation = None
    if has_couple:
        try:
            couple_relation = CoupleRelation.objects.filter(
                (models.Q(user1=request.user) & models.Q(user2=profile.couple.user)) |
                (models.Q(user1=profile.couple.user) & models.Q(user2=request.user))
            ).first()
        except:
            couple_relation = None
    
    context = {
        'user': request.user,
        'profile': profile,
        'sent_request': sent_request,  # 当前用户发送的请求
        'received_request': received_request,  # 当前用户收到的请求
        'has_couple': has_couple,
        'couple_relation': couple_relation
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

# 情侣测试API
@login_required
def couple_test_api(request):
    """
    获取情侣测试问题的API
    """
    try:
        # 获取分类参数
        category_id = request.GET.get('category_id')
        
        # 获取用户已回答的问题ID
        answered_question_ids = UserQuizAnswer.objects.filter(
            user=request.user
        ).values_list('question_id', flat=True)
        
        # 构建查询
        queryset = QuizQuestion.objects.exclude(
            id__in=answered_question_ids
        )
        
        # 如果指定了分类，按分类筛选
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # 随机获取20个未回答的问题
        questions = queryset.order_by('?')[:20]
        
        # 如果未回答的问题不足20个，获取所有问题
        if len(questions) < 20:
            queryset = QuizQuestion.objects
            if category_id:
                queryset = queryset.filter(category_id=category_id)
            questions = queryset.order_by('?')[:20]
        
        # 构建问题数据
        questions_data = []
        for question in questions:
            questions_data.append({
                'id': question.id,
                'question': question.question,
                'options': question.options,
                'category_id': question.category.id,
                'category_name': question.category.name
            })
        
        # 获取所有分类
        from .models import QuizCategory
        categories = QuizCategory.objects.all()
        categories_data = []
        for category in categories:
            categories_data.append({
                'id': category.id,
                'name': category.name,
                'description': category.description
            })
        
        return JsonResponse({
            'success': True,
            'questions': questions_data,
            'categories': categories_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@login_required
@require_http_methods(['POST'])
def submit_test_result(request):
    """
    提交情侣测试结果的API
    """
    try:
        # 解析请求数据
        answers = json.loads(request.POST.get('answers', '[]'))
        
        # 保存用户答案
        for answer in answers:
            question_id = answer.get('question_id')
            selected_option = answer.get('answer')
            
            if question_id and selected_option:
                # 获取问题
                question = QuizQuestion.objects.get(id=question_id)
                
                # 创建或更新用户答案
                user_answer, created = UserQuizAnswer.objects.get_or_create(
                    user=request.user,
                    question=question,
                    defaults={'selected_option': selected_option}
                )
                
                if not created:
                    user_answer.selected_option = selected_option
                    user_answer.save()
        
        # 生成测试分析（这里是模拟的分析结果）
        analysis = generate_test_analysis(answers)
        
        return JsonResponse({
            'success': True,
            'analysis': analysis
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


def generate_test_analysis(answers):
    """
    生成测试分析结果（模拟）
    """
    # 简单的模拟逻辑，实际项目中应该根据用户答案进行更复杂的分析
    import random
    
    # 随机生成匹配等级
    match_levels = ['非常匹配', '比较匹配', '一般匹配', '需要努力']
    match_level = random.choice(match_levels)
    
    # 根据匹配等级生成描述
    descriptions = {
        '非常匹配': '你们的关系充满了理解和支持，彼此尊重对方的意见和感受。在面对问题时，你们能够共同努力找到解决方案，展现出了很强的默契和团队精神。',
        '比较匹配': '你们的关系整体良好，虽然有时会有一些分歧，但能够通过沟通解决。继续加强彼此的理解和支持，你们的关系会更加稳固。',
        '一般匹配': '你们的关系存在一些需要注意的问题，在沟通和理解方面还有提升空间。建议多花时间了解对方的想法和感受，共同面对挑战。',
        '需要努力': '你们的关系面临一些挑战，在沟通方式和相互理解方面存在较大差异。建议双方坦诚交流，共同寻找改善关系的方法。'
    }
    
    # 生成建议
    advice = []
    if match_level == '非常匹配':
        advice = [
            '继续保持开放和诚实的沟通，这是维持健康关系的关键',
            '定期安排一些专属的约会时间，保持浪漫和激情',
            '学会接受和欣赏对方的不同之处，这会让你们的关系更加丰富'
        ]
    elif match_level == '比较匹配':
        advice = [
            '加强彼此之间的沟通，特别是在意见不合时',
            '多表达对对方的欣赏和感激之情',
            '共同参与一些新的活动，增进彼此的了解'
        ]
    elif match_level == '一般匹配':
        advice = [
            '学习更好的沟通技巧，避免争吵和冷战',
            '尝试从对方的角度看问题，增强同理心',
            '设定共同的目标，增强彼此的联系'
        ]
    else:  # 需要努力
        advice = [
            '考虑寻求专业的关系咨询帮助',
            '建立健康的沟通规则，避免指责和批评',
            '重新发现彼此的共同点，重建连接'
        ]
    
    return {
        'level': match_level,
        'description': descriptions[match_level],
        'advice': advice
    }


# 爱情故事视图
@login_required
def love_story_view(request):
    """爱情故事视图"""
    from .models import LoveStoryTimeline, MusicPlayer
    
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
    
    # 获取音乐播放器数据
    music_player = MusicPlayer.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'timeline_events': timeline_events,
        'partner_timeline_events': partner_timeline_events,
        'all_events': all_events,
        'music_player': music_player
    }
    
    return render(request, 'couple.html', context)


# 添加爱情故事视图
@login_required
def add_love_story(request):
    """添加爱情故事"""
    from .models import LoveStoryTimeline
    
    # 检查用户是否绑定情侣
    if not request.user.profile.couple:
        messages.error(request, '请先绑定情侣关系，才能添加爱情故事！')
        return redirect('couple_web:couple')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        date = request.POST.get('date')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        
        # 创建爱情故事时间轴事件
        LoveStoryTimeline.objects.create(
            user=request.user,
            title=title,
            date=date,
            description=description,
            image=image
        )
        
        messages.success(request, '爱情故事添加成功！')
        return redirect('couple_web:couple')
    
    return redirect('couple_web:couple')


# 添加音乐视图
@login_required
def add_music(request):
    """添加音乐"""
    from .models import MusicPlayer
    
    # 检查用户是否绑定情侣
    if not request.user.profile.couple:
        messages.error(request, '请先绑定情侣关系，才能添加音乐！')
        return redirect('couple_web:couple')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        artist = request.POST.get('artist')
        album_cover = request.FILES.get('album_cover')
        external_link = request.POST.get('external_link')
        
        # 创建音乐播放器记录
        MusicPlayer.objects.create(
            user=request.user,
            title=title,
            artist=artist,
            album_cover=album_cover,
            external_link=external_link
        )
        
        messages.success(request, '音乐添加成功！')
        return redirect('couple_web:couple')
    
    return redirect('couple_web:couple')


# 

# 情侣测试视图
@login_required
def couple_test_view(request):
    """情侣测试视图"""
    from core.models import Profile
    from .models import CoupleQuiz
    
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
    from core.models import Profile
    from .models import CouplePlace
    
    # 检查用户是否绑定情侣
    if not request.user.profile.couple:
        messages.error(request, '请先绑定情侣关系，才能使用情侣景点功能！')
        return redirect('couple_web:couple')
    
    # 从数据库获取情侣地点数据
    try:
        # 获取所有情侣地点，按创建时间倒序排序，限制前10个
        places = CouplePlace.objects.all().order_by('-created_at')[:10]
        
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
                'image': place.image.url if place.image else None,
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
    from .models import CouplePlace
    from django.http import JsonResponse
    
    try:
        # 获取分页参数
        page = int(request.GET.get('page', 1))
        page_size = 10  # 每页10条数据
        
        # 获取地点类型参数
        place_type = request.GET.get('place_type', '')
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 构建查询
        queryset = CouplePlace.objects.all().distinct()
        
        # 根据地点类型筛选
        if place_type and place_type != '全部地点':
            # 映射前端显示的类型到数据库存储的类型
            type_mapping = {
                '浪漫约会': 'romantic',
                '户外探险': 'outdoor',
                '文化体验': 'cultural',
                '美食餐厅': 'dining',
                '休闲娱乐': 'entertainment',
                '免费景点': 'free',
                '其他': 'other'
            }
            
            # 获取对应的数据库类型
            db_type = type_mapping.get(place_type)
            if db_type:
                queryset = queryset.filter(place_type=db_type)
        
        # 按创建时间倒序排序
        places = queryset.order_by('-created_at')[offset:offset + page_size]
        
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
                'image': place.image.url if place.image else None,
            }
            places_data.append(place_dict)
        
        # 检查是否还有更多数据
        has_more = queryset.count() > offset + page_size
        
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


# 情侣历史视图
@login_required
def couple_history_view(request):
    """情侣历史视图"""
    from .models import CoupleRelationHistory
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
    from .models import CoupleRelationHistory
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


# 纪念日管理API
@login_required
@require_http_methods(['POST'])
def add_anniversary(request):
    """添加纪念日"""
    from .models import Anniversary
    import json
    
    try:
        data = json.loads(request.body)
        
        anniversary = Anniversary.objects.create(
            user=request.user,
            title=data.get('title'),
            anniversary_date=data.get('anniversary_date'),
            anniversary_type=data.get('anniversary_type', 'custom'),
            description=data.get('description', ''),
            is_reminder_enabled=data.get('is_reminder_enabled', True),
            reminder_days=data.get('reminder_days', 1)
        )
        
        return JsonResponse({
            'success': True,
            'message': '纪念日添加成功',
            'anniversary': {
                'id': anniversary.id,
                'title': anniversary.title,
                'anniversary_date': anniversary.anniversary_date.strftime('%Y-%m-%d'),
                'anniversary_type': anniversary.anniversary_type,
                'description': anniversary.description,
                'is_reminder_enabled': anniversary.is_reminder_enabled,
                'reminder_days': anniversary.reminder_days,
                'created_at': anniversary.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'添加失败: {str(e)}'}, status=500)


@login_required
@require_http_methods(['PUT'])
def update_anniversary(request, anniversary_id):
    """更新纪念日"""
    from .models import Anniversary
    import json
    
    try:
        data = json.loads(request.body)
        anniversary = Anniversary.objects.get(id=anniversary_id, user=request.user)
        
        anniversary.title = data.get('title', anniversary.title)
        anniversary.anniversary_date = data.get('anniversary_date', anniversary.anniversary_date)
        anniversary.anniversary_type = data.get('anniversary_type', anniversary.anniversary_type)
        anniversary.description = data.get('description', anniversary.description)
        anniversary.is_reminder_enabled = data.get('is_reminder_enabled', anniversary.is_reminder_enabled)
        anniversary.reminder_days = data.get('reminder_days', anniversary.reminder_days)
        
        anniversary.save()
        
        return JsonResponse({
            'success': True,
            'message': '纪念日更新成功',
            'anniversary': {
                'id': anniversary.id,
                'title': anniversary.title,
                'anniversary_date': anniversary.anniversary_date.strftime('%Y-%m-%d'),
                'anniversary_type': anniversary.anniversary_type,
                'description': anniversary.description,
                'is_reminder_enabled': anniversary.is_reminder_enabled,
                'reminder_days': anniversary.reminder_days,
                'created_at': anniversary.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    except Anniversary.DoesNotExist:
        return JsonResponse({'success': False, 'message': '纪念日不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'更新失败: {str(e)}'}, status=500)


@login_required
@require_http_methods(['DELETE'])
def delete_anniversary(request, anniversary_id):
    """删除纪念日"""
    from .models import Anniversary
    
    try:
        anniversary = Anniversary.objects.get(id=anniversary_id, user=request.user)
        anniversary.delete()
        return JsonResponse({'success': True, 'message': '纪念日删除成功'})
    except Anniversary.DoesNotExist:
        return JsonResponse({'success': False, 'message': '纪念日不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'删除失败: {str(e)}'}, status=500)


@login_required
def get_anniversaries(request):
    """获取用户的纪念日列表"""
    from .models import Anniversary
    
    try:
        anniversaries = Anniversary.objects.filter(user=request.user).order_by('anniversary_date')
        
        anniversaries_data = []
        for anniversary in anniversaries:
            anniversaries_data.append({
                'id': anniversary.id,
                'title': anniversary.title,
                'anniversary_date': anniversary.anniversary_date.strftime('%Y-%m-%d'),
                'anniversary_type': anniversary.anniversary_type,
                'description': anniversary.description,
                'is_reminder_enabled': anniversary.is_reminder_enabled,
                'reminder_days': anniversary.reminder_days,
                'created_at': anniversary.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return JsonResponse({
            'success': True,
            'anniversaries': anniversaries_data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'获取失败: {str(e)}'}, status=500)


# 情侣设置视图
@login_required
def couple_settings(request):
    """保存情侣设置"""
    from core.models import Profile
    from couple.models import CoupleRelation
    
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
                profile.save()
            
            # 保存CoupleRelation数据
            if profile.couple:
                # 获取或创建CoupleRelation记录
                try:
                    relation = CoupleRelation.objects.filter(
                        (models.Q(user1=request.user) & models.Q(user2=profile.couple.user)) |
                        (models.Q(user1=profile.couple.user) & models.Q(user2=request.user))
                    ).first()
                    
                    if relation:
                        # 更新基本信息
                        relation.couple_name = request.POST.get('couple_name')
                        relation.love_story = request.POST.get('love_story')
                        relation.love_vow = request.POST.get('love_vow')
                        
                        # 更新主题设置
                        relation.theme = request.POST.get('theme', 'light_love')
                        relation.primary_color = request.POST.get('primary_color', '#FF6B8B')
                        relation.secondary_color = request.POST.get('secondary_color', '#722ED1')
                        
                        # 更新隐私设置
                        relation.visibility = request.POST.get('visibility', 'only_me')
                        relation.show_couple_dynamics = request.POST.get('show_couple_dynamics') == 'on'
                        relation.show_anniversary = request.POST.get('show_anniversary') == 'on'
                        relation.show_gifts = request.POST.get('show_gifts') == 'on'
                        
                        # 更新消息提醒设置
                        relation.notify_partner_messages = request.POST.get('notify_partner_messages') == 'on'
                        relation.notify_dynamics = request.POST.get('notify_dynamics') == 'on'
                        relation.notify_anniversary = request.POST.get('notify_anniversary') == 'on'
                        
                        # 更新恋爱纪念日
                        if anniversary:
                            relation.relationship_start_date = anniversary_date
                        
                        relation.save()
                    else:
                        try:
                            # 确保有恋爱纪念日
                            if not anniversary:
                                # 如果没有提供恋爱纪念日，使用当前日期
                                from django.utils import timezone
                                anniversary_date = timezone.now().date()
                            
                            relation = CoupleRelation.objects.create(
                                user1=request.user,
                                user2=profile.couple.user,
                                couple_name=request.POST.get('couple_name'),
                                love_story=request.POST.get('love_story'),
                                love_vow=request.POST.get('love_vow'),
                                theme=request.POST.get('theme', 'light_love'),
                                primary_color=request.POST.get('primary_color', '#FF6B8B'),
                                secondary_color=request.POST.get('secondary_color', '#722ED1'),
                                visibility=request.POST.get('visibility', 'only_me'),
                                show_couple_dynamics=request.POST.get('show_couple_dynamics') == 'on',
                                show_anniversary=request.POST.get('show_anniversary') == 'on',
                                show_gifts=request.POST.get('show_gifts') == 'on',
                                notify_partner_messages=request.POST.get('notify_partner_messages') == 'on',
                                notify_dynamics=request.POST.get('notify_dynamics') == 'on',
                                notify_anniversary=request.POST.get('notify_anniversary') == 'on',
                                relationship_start_date=anniversary_date
                            )
                        except Exception as e:
                            print(f"Error creating CoupleRelation: {e}")
                except Exception as e:
                    print(f"Error updating CoupleRelation: {e}")
            
            messages.success(request, '设置已保存')
        except Exception as e:
            messages.error(request, f'保存设置失败: {str(e)}')
    
    return redirect('couple_web:couple')