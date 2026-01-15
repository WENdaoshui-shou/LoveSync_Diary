from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from core.models import User
from .models import Follow
from moment.models import Moment
from photo.models import Photo

@login_required
def profile(request, user_id):
    """用户主页"""
    # 获取用户信息
    profile_user = get_object_or_404(User, id=user_id)
    
    # 获取当前用户是否已关注该用户
    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(
            follower=request.user,
            following=profile_user,
            is_deleted=False
        ).exists()
    
    # 获取粉丝数和关注数
    followers_count = Follow.objects.filter(following=profile_user, is_deleted=False).count()
    print(f"DEBUG: followers_count = {followers_count}")
    following_count = Follow.objects.filter(follower=profile_user, is_deleted=False).count()
    print(f"DEBUG: following_count = {following_count}")
    
    # 获取动态列表
    moments = Moment.objects.filter(
        user=profile_user
    ).order_by('-created_at')
    
    # 获取相册图片
    photos = Photo.objects.filter(
        user=profile_user
    ).order_by('-uploaded_at')
    
    context = {
        'profile_user': profile_user,
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count,
        'moments': moments,
        'photos': photos,
        'unread_count': 0,  # 可根据实际情况添加未读消息数
    }
    print(context)
    
    return render(request, 'user/profile.html', context)

@login_required
def follow(request):
    """关注用户"""
    if request.method == 'POST':
        following_id = request.POST.get('following_id')
        
        try:
            following_user = User.objects.get(id=following_id)
            
            # 不能关注自己
            if request.user == following_user:
                return JsonResponse({'success': False, 'message': '不能关注自己'})
            
            # 检查是否已经关注
            follow_obj, created = Follow.objects.get_or_create(
                follower=request.user,
                following=following_user,
                defaults={'is_deleted': False}
            )
            
            if not created:
                # 如果已经关注但is_deleted为True，则恢复关注
                if follow_obj.is_deleted:
                    follow_obj.is_deleted = False
                    follow_obj.save()
                    success = True
                    message = f'已关注 {following_user.name}'
                else:
                    success = False
                    message = '已经关注过该用户'
            else:
                success = True
                message = f'已关注 {following_user.name}'
            
            # 获取更新后的粉丝数
            followers_count = Follow.objects.filter(following=following_user, is_deleted=False).count()
            
            return JsonResponse({
                'success': success,
                'message': message,
                'followers_count': followers_count,
                'is_following': True
            })
            
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': '用户不存在'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'关注失败：{str(e)}'})
    
    return JsonResponse({'success': False, 'message': '请求方式错误'})

@login_required
def unfollow(request):
    """取消关注"""
    if request.method == 'POST':
        following_id = request.POST.get('following_id')
        
        try:
            following_user = User.objects.get(id=following_id)
            
            # 检查是否已经关注
            follow_obj = Follow.objects.filter(
                follower=request.user,
                following=following_user,
                is_deleted=False
            ).first()
            
            if follow_obj:
                # 软删除
                follow_obj.is_deleted = True
                follow_obj.save()
                success = True
                message = f'已取消关注 {following_user.name}'
            else:
                success = False
                message = '未关注该用户'
            
            # 获取更新后的粉丝数
            followers_count = Follow.objects.filter(following=following_user, is_deleted=False).count()
            
            return JsonResponse({
                'success': success,
                'message': message,
                'followers_count': followers_count,
                'is_following': False
            })
            
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': '用户不存在'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'取消关注失败：{str(e)}'})
    
    return JsonResponse({'success': False, 'message': '请求方式错误'})

@login_required
def get_followers(request, user_id):
    """获取粉丝列表"""
    profile_user = get_object_or_404(User, id=user_id)
    followers = Follow.objects.filter(
        following=profile_user,
        is_deleted=False
    ).select_related('follower').order_by('-created_at')[:10]  # 只返回前10个
    
    followers_data = []
    for follow_obj in followers:
        followers_data.append({
            'id': follow_obj.follower.id,
            'name': follow_obj.follower.name,
            'avatar': follow_obj.follower.profile.userAvatar.url,
        })
    
    return JsonResponse({'success': True, 'followers': followers_data})

@login_required
def get_following(request, user_id):
    """获取关注列表"""
    profile_user = get_object_or_404(User, id=user_id)
    following = Follow.objects.filter(
        follower=profile_user,
        is_deleted=False
    ).select_related('following').order_by('-created_at')[:10]  # 只返回前10个
    
    following_data = []
    for follow_obj in following:
        following_data.append({
            'id': follow_obj.following.id,
            'name': follow_obj.following.name,
            'avatar': follow_obj.following.profile.userAvatar.url,
        })
    
    return JsonResponse({'success': True, 'following': following_data})

@login_required
def load_more_moments(request, user_id):
    """加载更多动态"""
    if request.method == 'GET':
        page = request.GET.get('page', 2)  # 默认从第2页开始加载
        
        profile_user = get_object_or_404(User, id=user_id)
        moments = Moment.objects.filter(
            user=profile_user
        ).order_by('-created_at')
        
        paginator = Paginator(moments, 10)  # 每页10条
        
        try:
            moments_page = paginator.page(page)
        except PageNotAnInteger:
            moments_page = paginator.page(2)
        except EmptyPage:
            return JsonResponse({'success': False, 'message': '没有更多动态了'})
        
        # 构建动态数据
        moments_data = []
        for moment in moments_page:
            moments_data.append({
                'id': moment.id,
                'content': moment.content,
                'created_at': moment.created_at.strftime('%Y-%m-%d %H:%M'),
                'likes_count': moment.likes,
                'comments_count': moment.comments,
                'images': [img.image.url for img in moment.moment_images.all()],
            })
        
        return JsonResponse({
            'success': True,
            'moments': moments_data,
            'has_next': moments_page.has_next(),
            'next_page': moments_page.next_page_number() if moments_page.has_next() else None
        })
    
    return JsonResponse({'success': False, 'message': '请求方式错误'})