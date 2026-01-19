from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from core.models import User, CouplePlace as Place
from .models import Follow, Collection
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
    following_count = Follow.objects.filter(follower=profile_user, is_deleted=False).count()
    
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
    ).select_related('following').order_by('-created_at')
    
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


@login_required
def add_collection(request):
    """添加收藏"""
    if request.method == 'POST':
        try:
            # 获取参数
            content_type = request.POST.get('content_type')
            object_id = request.POST.get('object_id')
            
            # 参数验证
            if not content_type or not object_id:
                return JsonResponse({'success': False, 'message': '参数错误'})
            
            # 验证收藏类型
            if content_type not in ['moment', 'place']:
                return JsonResponse({'success': False, 'message': '无效的收藏类型'})
            
            # 验证收藏对象是否存在
            if content_type == 'moment':
                # 检查动态是否存在
                try:
                    moment = Moment.objects.get(id=object_id)
                except Moment.DoesNotExist:
                    return JsonResponse({'success': False, 'message': '动态不存在'})
            else:
                # 检查地点是否存在
                try:
                    place = Place.objects.get(id=object_id)
                except Place.DoesNotExist:
                    return JsonResponse({'success': False, 'message': '地点不存在'})
            
            # 尝试创建收藏
            collection, created = Collection.objects.get_or_create(
                user=request.user,
                content_type=content_type,
                object_id=object_id
            )
            
            if created:
                return JsonResponse({'success': True, 'message': '收藏成功'})
            else:
                return JsonResponse({'success': False, 'message': '已收藏'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'收藏失败：{str(e)}'})
    
    return JsonResponse({'success': False, 'message': '请求方式错误'})


@login_required
def remove_collection(request):
    """取消收藏"""
    if request.method == 'POST':
        try:
            # 获取参数
            content_type = request.POST.get('content_type')
            object_id = request.POST.get('object_id')
            
            # 参数验证
            if not content_type or not object_id:
                return JsonResponse({'success': False, 'message': '参数错误'})
            
            # 验证收藏类型
            if content_type not in ['moment', 'place']:
                return JsonResponse({'success': False, 'message': '无效的收藏类型'})
            
            # 查找并删除收藏
            collection = Collection.objects.filter(
                user=request.user,
                content_type=content_type,
                object_id=object_id
            ).first()
            
            if collection:
                collection.delete()
                return JsonResponse({'success': True, 'message': '取消收藏成功'})
            else:
                return JsonResponse({'success': False, 'message': '未收藏'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'取消收藏失败：{str(e)}'})
    
    return JsonResponse({'success': False, 'message': '请求方式错误'})


@login_required
def get_collections(request):
    """获取收藏列表"""
    if request.method == 'GET':
        try:
            # 获取参数
            content_type = request.GET.get('content_type')
            page = request.GET.get('page', 1)
            page_size = 10
            
            # 查询条件
            query = Collection.objects.filter(user=request.user)
            
            # 如果指定了收藏类型
            if content_type:
                if content_type not in ['moment', 'place']:
                    return JsonResponse({'success': False, 'message': '无效的收藏类型'})
                query = query.filter(content_type=content_type)
            
            # 按收藏时间倒序排序
            collections = query.order_by('-created_at')
            
            # 分页处理
            paginator = Paginator(collections, page_size)
            try:
                page_obj = paginator.page(page)
            except PageNotAnInteger:
                page_obj = paginator.page(1)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)
            
            # 构建响应数据
            moments = []
            places = []
            
            for collection in page_obj:
                if collection.content_type == 'moment':
                    # 获取动态信息
                    try:
                        moment = Moment.objects.get(id=collection.object_id)
                        moments.append({
                            'id': moment.id,
                            'user_id': moment.user.id,
                            'user_name': moment.user.name,
                            'user_avatar': moment.user.profile.userAvatar.url if moment.user.profile.userAvatar else None,
                            'content': moment.content,
                            'images': [img.image.url for img in moment.moment_images.all()],
                            'created_at': moment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                            'likes': moment.likes,
                            'comments': moment.comments,
                            'collected_at': collection.created_at.strftime('%Y-%m-%d %H:%M:%S')
                        })
                    except Moment.DoesNotExist:
                        pass  # 动态不存在，跳过
                else:
                    # 获取地点信息
                    try:
                        place = Place.objects.get(id=collection.object_id)
                        places.append({
                            'id': place.id,
                            'name': place.name,
                            'description': place.description,
                            'image_url': place.image_url,
                            'place_type': place.place_type,
                            'rating': place.rating,
                            'price_range': place.price_range,
                            'address': place.address,
                            'review_count': place.review_count,
                            'collected_at': collection.created_at.strftime('%Y-%m-%d %H:%M:%S')
                        })
                    except Place.DoesNotExist:
                        pass  # 地点不存在，跳过
            
            return JsonResponse({
                'success': True,
                'moments': moments,
                'places': places,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'获取收藏列表失败：{str(e)}'})
    
    return JsonResponse({'success': False, 'message': '请求方式错误'})


@login_required
def collections(request):
    """收藏页面"""
    try:
        # 获取用户收藏的动态
        moment_collections = Collection.objects.filter(
            user=request.user,
            content_type='moment'
        ).order_by('-created_at')
        
        # 获取用户收藏的地点
        place_collections = Collection.objects.filter(
            user=request.user,
            content_type='place'
        ).order_by('-created_at')
        
        # 获取动态详情
        moments = []
        for collection in moment_collections:
            try:
                moment = Moment.objects.get(id=collection.object_id)
                moments.append({
                    'id': moment.id,
                    'user_id': moment.user.id,
                    'user_name': moment.user.name,
                    'user_avatar': moment.user.profile.userAvatar.url if moment.user.profile.userAvatar else None,
                    'content': moment.content,
                    'images': [img.image.url for img in moment.moment_images.all()],
                    'created_at': moment.created_at,
                    'likes': moment.likes,
                    'comments': moment.comments,
                    'collected_at': collection.created_at
                })
            except Moment.DoesNotExist:
                pass  # 动态不存在，跳过
        
        # 获取地点详情
        places = []
        for collection in place_collections:
            try:
                place = Place.objects.get(id=collection.object_id)
                places.append({
                    'id': place.id,
                    'name': place.name,
                    'description': place.description,
                    'image_url': place.image_url,
                    'place_type': place.place_type,
                    'rating': place.rating,
                    'price_range': place.price_range,
                    'address': place.address,
                    'review_count': place.review_count,
                    'collected_at': collection.created_at
                })
            except Place.DoesNotExist:
                pass  # 地点不存在，跳过
        
        # 获取未读消息数
        try:
            from message.models import Message
            unread_count = Message.objects.filter(
                user=request.user,
                is_read=False,
                is_deleted=False
            ).count()
        except ImportError:
            unread_count = 0
        
        context = {
            'moments': moments,
            'places': places,
            'unread_count': unread_count
        }
        
        return render(request, 'user/collections.html', context)
        
    except Exception as e:
        messages.error(request, f'加载收藏页面失败：{str(e)}')
        return render(request, 'user/collections.html', {
            'moments': [],
            'places': [],
            'unread_count': 0
        })