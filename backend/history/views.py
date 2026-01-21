from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import History
from django.utils import timezone
from django.core.paginator import Paginator
import json


@login_required
def history_index(request):
    """历史记录首页"""
    # 获取用户的历史记录，按浏览时间倒序排列
    histories = History.objects.filter(user=request.user).order_by('-viewed_at')
    
    # 分页处理，每页显示10条
    paginator = Paginator(histories, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # 为每个历史记录添加目标详情
    enhanced_histories = []
    for history in page_obj.object_list:
        # 添加基本信息
        history_info = {
            'id': history.id,
            'history_type': history.history_type,
            'target_id': history.target_id,
            'viewed_at': history.viewed_at,
        }

        try:
            if history.history_type == 'moment':
                from moment.models import Moment
                moment = Moment.objects.get(id=history.target_id)
                history_info.update({
                    'title': moment.content[:50] + '...' if len(moment.content) > 50 else moment.content,
                    'username': getattr(moment.user, 'name', '用户'),
                    'user_avatar': moment.user.profile.userAvatar.url if hasattr(moment.user, 'profile') and getattr(moment.user.profile, 'userAvatar', None) else '',
                    'content': moment.content,
                    'image_url': moment.moment_images.first().image.url if hasattr(moment, 'moment_images') and moment.moment_images.exists() else '',
                    'likes': getattr(moment, 'likes', 0),
                    'comments': getattr(moment, 'comments', 0),
                })
                enhanced_histories.append(history_info)
            elif history.history_type == 'user':
                from core.models import User
                user = User.objects.get(id=history.target_id)
                history_info.update({
                    'username': getattr(user, 'name', '用户'),
                    'user_avatar': user.profile.userAvatar.url if hasattr(user, 'profile') and getattr(user.profile, 'userAvatar', None) else '',
                    'bio': user.profile.bio if hasattr(user, 'profile') and getattr(user.profile, 'bio', None) else '这个人很懒，什么都没写',
                })
                enhanced_histories.append(history_info)
        except Exception:
            pass
    
    context = {
        'histories': enhanced_histories,
        'page_obj': page_obj,
        'has_next': page_obj.has_next(),
        'total_count': len(enhanced_histories),
        'moment_count': sum(1 for h in enhanced_histories if h['history_type'] == 'moment'),
        'user_count': sum(1 for h in enhanced_histories if h['history_type'] == 'user'),
    }
    
    return render(request, 'history/history_index.html', context)


@login_required
def add_history(request):
    """添加浏览历史记录"""
    if request.method == 'POST':
        try:
            # 解析POST数据
            data = json.loads(request.body)
            history_type = data.get('history_type')
            target_id = data.get('target_id')
            
            # 验证数据
            if not history_type or not target_id:
                return JsonResponse({'success': False, 'message': '缺少必要参数'}, status=400)
            
            if history_type not in ['moment', 'user']:
                return JsonResponse({'success': False, 'message': '无效的历史类型'}, status=400)
            
            # 尝试获取现有历史记录
            history, created = History.objects.get_or_create(
                user=request.user,
                history_type=history_type,
                target_id=target_id
            )
            
            # 如果记录已存在，更新浏览时间
            if not created:
                history.viewed_at = timezone.now()
                history.save()
            
            return JsonResponse({'success': True, 'message': '历史记录添加成功'})
        
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': '无效的JSON数据'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'message': '只支持POST请求'}, status=405)


@login_required
def load_more_history(request):
    """加载更多历史记录（用于无限滚动）"""
    if request.method == 'GET':
        try:
            # 获取分页参数
            page = int(request.GET.get('page', 1))
            per_page = 10
            
            # 获取用户的历史记录，按浏览时间倒序排列
            histories = History.objects.filter(user=request.user).order_by('-viewed_at')
            
            # 分页处理
            paginator = Paginator(histories, per_page)
            page_obj = paginator.get_page(page)
            
            # 准备返回的数据
            history_data = []
            for history in page_obj.object_list:
                # 根据历史类型获取对应的目标信息
                history_info = {
                    'id': history.id,
                    'history_type': history.history_type,
                    'target_id': history.target_id,
                    'viewed_at': history.viewed_at.strftime('%Y-%m-%d %H:%M:%S'),
                }
                
                try:
                    if history.history_type == 'moment':
                        from moment.models import Moment
                        moment = Moment.objects.get(id=history.target_id)
                        history_info.update({
                            'title': moment.content[:50] + '...' if len(moment.content) > 50 else moment.content,
                            'username': getattr(moment.user, 'name', '用户'),
                            'user_avatar': moment.user.profile.userAvatar.url if hasattr(moment.user, 'profile') and getattr(moment.user.profile, 'userAvatar', None) else '',
                            'content': moment.content,
                            'image_url': moment.moment_images.first().image.url if hasattr(moment, 'moment_images') and moment.moment_images.exists() else '',
                            'likes': getattr(moment, 'likes', 0),
                            'comments': getattr(moment, 'comments', 0),
                        })
                        history_data.append(history_info)
                    elif history.history_type == 'user':
                        from core.models import User
                        user = User.objects.get(id=history.target_id)
                        history_info.update({
                            'username': getattr(user, 'name', '用户'),
                            'user_avatar': user.profile.userAvatar.url if hasattr(user, 'profile') and getattr(user.profile, 'userAvatar', None) else '',
                            'bio': user.profile.bio if hasattr(user, 'profile') and getattr(user.profile, 'bio', None) else '这个人很懒，什么都没写',
                        })
                        history_data.append(history_info)
                except Exception:
                    # 如果获取目标详情失败，跳过该历史记录
                    pass
            
            return JsonResponse({
                'success': True,
                'histories': history_data,
                'has_next': page_obj.has_next() and len(history_data) > 0,
                'next_page': page + 1 if page_obj.has_next() and len(history_data) > 0 else None,
                'total_count': len(history_data),
                'moment_count': sum(1 for h in history_data if h['history_type'] == 'moment'),
                'user_count': sum(1 for h in history_data if h['history_type'] == 'user'),
            })
        
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'message': '只支持GET请求'}, status=405)
