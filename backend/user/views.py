from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from core.models import User
from couple.models import CouplePlace as Place
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
                # 清除缓存
                try:
                    from django.core.cache import caches
                    master_cache = caches['master_cache']  # 使用社区缓存数据库 1
                    user_id = request.user.id
                    # 清除收藏列表缓存（包括API和页面缓存）
                    master_cache.delete_pattern(f'user:collections:{user_id}*')
                    master_cache.delete_pattern(f'user:collections:page:{user_id}*')
                except Exception as e:
                    print(f"缓存清除失败: {e}")
                
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
                # 清除缓存
                try:
                    from django.core.cache import caches
                    master_cache = caches['master_cache']  # 使用社区缓存数据库 1
                    user_id = request.user.id
                    # 清除收藏列表缓存（包括API和页面缓存）
                    master_cache.delete_pattern(f'user:collections:{user_id}*')
                    master_cache.delete_pattern(f'user:collections:page:{user_id}*')
                except Exception as e:
                    print(f"缓存清除失败: {e}")
                
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
            
            # 生成缓存键
            user_id = request.user.id
            if content_type:
                cache_key = f'user:collections:{user_id}:{content_type}:{page}'
            else:
                cache_key = f'user:collections:{user_id}:all:{page}'
            
            # 尝试从缓存获取
            cached_result = None
            try:
                from django.core.cache import caches
                master_cache = caches['master_cache']  # 使用社区缓存数据库 1
                cached_result = master_cache.get(cache_key)
                if cached_result:
                    return JsonResponse(cached_result)
            except Exception as e:
                print(f"缓存读取失败: {e}")
            
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
                            'image_url': place.image.url if place.image else None,
                            'place_type': place.get_place_type_display(),
                            'rating': place.rating,
                            'price_range': place.price_range,
                            'address': place.address,
                            'review_count': place.review_count,
                            'collected_at': collection.created_at.strftime('%Y-%m-%d %H:%M:%S')
                        })
                    except Place.DoesNotExist:
                        pass  # 地点不存在，跳过
            
            # 构建响应数据
            response_data = {
                'success': True,
                'moments': moments,
                'places': places,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages
            }
            
            # 缓存结果，有效期5分钟
            try:
                from django.core.cache import caches
                master_cache = caches['master_cache']  # 使用社区缓存数据库 1
                master_cache.set(cache_key, response_data, 300)
            except Exception as e:
                print(f"缓存写入失败: {e}")
            
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'获取收藏列表失败：{str(e)}'})
    
    return JsonResponse({'success': False, 'message': '请求方式错误'})


@login_required
def collections(request):
    """收藏页面"""
    try:
        # 生成缓存键
        user_id = request.user.id
        cache_key = f'user:collections:page:{user_id}'
        
        # 尝试从缓存获取
        cached_context = None
        try:
            from django.core.cache import caches
            master_cache = caches['master_cache']  # 使用社区缓存数据库 1
            cached_context = master_cache.get(cache_key)
            if cached_context:
                return render(request, 'user/collections.html', cached_context)
        except Exception as e:
            print(f"缓存读取失败: {e}")
        
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
                    'image': place.image.url if place.image else None,
                    'place_type': place.get_place_type_display(),
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
        
        # 缓存结果，有效期5分钟
        try:
            from django.core.cache import caches
            master_cache = caches['master_cache']  # 使用社区缓存数据库 1
            master_cache.set(cache_key, context, 300)
        except Exception as e:
            print(f"缓存写入失败: {e}")
        
        return render(request, 'user/collections.html', context)
        
    except Exception as e:
        messages.error(request, f'加载收藏页面失败：{str(e)}')
        return render(request, 'user/collections.html', {
            'moments': [],
            'places': [],
            'unread_count': 0
        })


# 关注/取消关注接口
@login_required
def follow_toggle(request):
    """关注/取消关注接口，支持 AJAX"""
    if request.method == 'POST':
        followed_id = request.POST.get('followed_id')
        if not followed_id:
            return JsonResponse({'success': False, 'message': '缺少被关注用户ID'}, status=400)
        
        try:
            followed = User.objects.get(id=followed_id)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': '被关注用户不存在'}, status=404)
        
        # 禁止用户关注自己
        if followed == request.user:
            return JsonResponse({'success': False, 'message': '不能关注自己'}, status=400)
        
        # 使用 get_or_create 判断关注状态，考虑软删除
        follow_obj, created = Follow.objects.get_or_create(
            follower=request.user,
            following=followed,
            defaults={'is_deleted': False}
        )
        
        if created or follow_obj.is_deleted:
            # 关注成功
            follow_obj.is_deleted = False
            follow_obj.save()
            
            # 获取更新后的粉丝数
            followers_count = Follow.objects.filter(following=followed, is_deleted=False).count()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': '关注成功',
                    'is_following': True,
                    'followers_count': followers_count
                })
            messages.success(request, '关注成功')
        else:
            # 取消关注
            follow_obj.is_deleted = True
            follow_obj.save()
            
            # 获取更新后的粉丝数
            followers_count = Follow.objects.filter(following=followed, is_deleted=False).count()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': '取消关注成功',
                    'is_following': False,
                    'followers_count': followers_count
                })
            messages.success(request, '取消关注成功')
    
    # 如果不是POST请求，重定向到个人主页
    from django.urls import reverse
    return redirect(reverse('core:personal_center'))

# 关注列表页面
@login_required
def following_list(request):
    """我的关注列表页面"""
    # 查询当前用户关注的所有用户
    follows = Follow.objects.filter(follower=request.user, is_deleted=False).select_related('following').order_by('-created_at')
    
    # 构建包含用户信息和关注时间的数据结构
    user_with_follow_status = []
    for follow in follows:
        user_with_follow_status.append({
            'user': follow.following,
            'follow_time': follow.created_at,
            'is_following': True  # 关注列表中的用户肯定是已关注的
        })
    
    # 统计关注数和粉丝数
    following_count = follows.count()
    follower_count = Follow.objects.filter(following=request.user, is_deleted=False).count()
    
    context = {
        'page_title': '我的关注',   
        'user_list': user_with_follow_status,
        'list_type': 'following',
        'follows': follows,
        'following_count': following_count,
        'follower_count': follower_count
    }
    
    return render(request, 'community/follow_list_fixed.html', context)

# 粉丝列表页面
@login_required
def follower_list(request):
    """我的粉丝列表页面"""
    # 查询关注当前用户的所有用户
    follows = Follow.objects.filter(following=request.user, is_deleted=False).select_related('follower').order_by('-created_at')
    
    # 构建包含用户信息和关注时间的数据结构
    user_with_follow_status = []
    for follow in follows:
        # 判断当前用户是否也关注了粉丝（互相关注）
        is_following_back = Follow.objects.filter(follower=request.user, following=follow.follower, is_deleted=False).exists()
        
        user_with_follow_status.append({
            'user': follow.follower,
            'follow_time': follow.created_at,
            'is_following': is_following_back  # 标记是否已回关
        })
    
    # 统计关注数和粉丝数
    following_count = Follow.objects.filter(follower=request.user, is_deleted=False).count()
    follower_count = follows.count()
    
    context = {
        'page_title': '我的粉丝',
        'user_list': user_with_follow_status,
        'list_type': 'followers',
        'follows': follows,
        'following_count': following_count,
        'follower_count': follower_count
    }
    
    return render(request, 'community/follow_list_fixed.html', context)

# 用户主页
def user_profile(request, username):
    """用户主页，显示关注按钮"""
    # 获取目标用户对象
    target_user = get_object_or_404(User, username=username)
    
    # 判断当前用户是否关注目标用户
    is_following = Follow.objects.filter(follower=request.user, following=target_user, is_deleted=False).exists()
    
    # 统计目标用户的关注数、粉丝数
    following_count = Follow.objects.filter(follower=target_user, is_deleted=False).count()
    follower_count = Follow.objects.filter(following=target_user, is_deleted=False).count()
    
    # 获取目标用户的动态数量
    from moment.models import Moment
    moment_count = Moment.objects.filter(user=target_user).count()
    
    # 获取情侣信息
    partner = None
    couple_relation = None
    love_vow = None
    
    if target_user.profile.couple:
        partner = target_user.profile.couple.user
        # 获取情侣关系
        from couple.models import CoupleRelation
        from django.db.models import Q
        couple_relation = CoupleRelation.objects.filter(
            (Q(user1=target_user) & Q(user2=partner)) |
            (Q(user1=partner) & Q(user2=target_user))
        ).first()
        
        # 获取爱情誓言
        if couple_relation and couple_relation.love_vow:
            love_vow = couple_relation.love_vow
    
    # 获取爱情故事时间轴
    love_story_timeline = []
    from couple.models import LoveStoryTimeline
    timeline_events = LoveStoryTimeline.objects.filter(user=target_user).order_by('-date')
    
    # 获取伴侣的爱情故事时间轴
    partner_timeline_events = []
    if partner:
        partner_timeline_events = LoveStoryTimeline.objects.filter(user=partner).order_by('-date')
    
    # 合并并按日期排序
    all_events = list(timeline_events) + list(partner_timeline_events)
    all_events.sort(key=lambda x: x.date, reverse=True)
    love_story_timeline = all_events
    
    # 获取音乐播放器数据
    music_player = []
    from couple.models import MusicPlayer
    music_player = MusicPlayer.objects.filter(user=target_user).order_by('-created_at')[:5]
    
    context = {
        'target_user': target_user,
        'is_following': is_following,
        'following_count': following_count,
        'follower_count': follower_count,
        'partner': partner,
        'couple_relation': couple_relation,
        'love_vow': love_vow,
        'love_story_timeline': love_story_timeline,
        'music_player': music_player,
        'stats': {
            'moment_count': moment_count
        }
    }

    return render(request, 'community/user_profile.html', context)

# 成就页面
@login_required
def achievements_view(request):
    """成就页面"""
    return render(request, 'achievements.html', {
        'user': request.user
    })

# 成就数据API视图
@login_required
def get_achievements_data(request):
    """获取用户成就数据"""
    from user.models import Achievement, UserAchievement
    
    # 获取用户的所有成就
    user_achievements = UserAchievement.objects.filter(user=request.user).select_related('achievement')
    
    # 构建成就数据
    achievements_data = []
    for ua in user_achievements:
        achievement = ua.achievement
        achievements_data.append({
            'id': achievement.id,
            'title': achievement.title,
            'description': achievement.description,
            'icon': achievement.icon,
            'unlocked': ua.unlocked,
            'date': ua.unlocked_at.strftime('%Y-%m-%d') if ua.unlocked_at else None,
            'progress': ua.progress
        })
    
    # 计算统计数据
    total = Achievement.objects.count()
    unlocked = len([a for a in achievements_data if a['unlocked']])
    completion_rate = round((unlocked / total) * 100) if total > 0 else 0
    recent_unlocked = len([a for a in achievements_data if a['unlocked']])
    
    # 构建响应数据
    response_data = {
        'achievements': achievements_data,
        'stats': {
            'totalAchievements': total,
            'unlockedAchievements': unlocked,
            'completionRate': completion_rate,
            'recentAchievements': recent_unlocked
        }
    }
    
    import json
    from django.http import HttpResponse
    return HttpResponse(json.dumps(response_data), content_type='application/json')

def get_recommended_users(request):
    """获取推荐关注的用户"""
    # 获取当前用户
    current_user = request.user
    
    # 获取当前用户已经关注的用户
    followed_users = []
    if request.user.is_authenticated:
        followed_users = Follow.objects.filter(
            follower=current_user,
            is_deleted=False
        ).values_list('following_id', flat=True)
    
    # 获取推荐用户：排除已关注的用户
    recommended_users_query = User.objects.all()
    
    # 如果用户已登录，排除自己和已关注的用户
    if request.user.is_authenticated:
        recommended_users_query = recommended_users_query.exclude(
            id__in=[current_user.id] + list(followed_users)
        )
    
    recommended_users = recommended_users_query[:10]
    
    # 构建推荐用户数据
    recommended_users_data = []
    for user in recommended_users:
        try:
            # 计算粉丝数
            followers_count = Follow.objects.filter(
                following=user,
                is_deleted=False
            ).count()
            
            # 安全获取头像URL
            avatar_url = None
            if hasattr(user, 'profile') and hasattr(user.profile, 'userAvatar') and user.profile.userAvatar:
                avatar_url = user.profile.userAvatar.url
            
            # 安全获取简介
            bio = ''
            if hasattr(user, 'profile') and hasattr(user.profile, 'bio'):
                bio = user.profile.bio or ''
            
            recommended_users_data.append({
                'id': user.id,
                'name': user.name,
                'avatar': avatar_url,
                'followers_count': followers_count,
                'bio': bio
            })
        except Exception as e:
            print(f"处理用户 {user.id} 时出错: {str(e)}")
            continue
    
    return JsonResponse({'success': True, 'recommended_users': recommended_users_data})

def get_hot_couples(request):
    """获取热门情侣"""
    from django.db.models import Sum
    
    # 获取有情侣关系的用户
    coupled_users = User.objects.filter(profile__couple__isnull=False)
    
    # 构建情侣数据
    couples_data = []
    processed_couples = set()
    
    for user in coupled_users:
        try:
            # 获取情侣对象
            if not hasattr(user, 'profile') or not hasattr(user.profile, 'couple') or not user.profile.couple:
                continue
            
            couple = user.profile.couple
            
            # 获取情侣双方
            user1 = user
            user2 = couple.user
            
            # 排除包含当前用户的情侣
            if request.user.is_authenticated and (user1.id == request.user.id or user2.id == request.user.id):
                continue
            
            # 避免重复处理
            couple_key = frozenset([user1.id, user2.id])
            if couple_key in processed_couples:
                continue
            processed_couples.add(couple_key)
            
            # 计算双方粉丝数
            user1_followers = Follow.objects.filter(following=user1, is_deleted=False).count()
            user2_followers = Follow.objects.filter(following=user2, is_deleted=False).count()
            total_followers = user1_followers + user2_followers
            
            # 安全获取用户1头像
            user1_avatar = None
            if hasattr(user1, 'profile') and hasattr(user1.profile, 'userAvatar') and user1.profile.userAvatar:
                user1_avatar = user1.profile.userAvatar.url
            
            # 安全获取用户2头像
            user2_avatar = None
            if hasattr(user2, 'profile') and hasattr(user2.profile, 'userAvatar') and user2.profile.userAvatar:
                user2_avatar = user2.profile.userAvatar.url
            
            # 尝试获取爱情誓言
            love_vow = ''
            try:
                from couple.models import CoupleRelation
                from django.db.models import Q
                couple_relation = CoupleRelation.objects.filter(
                    (Q(user1=user1) & Q(user2=user2)) |
                    (Q(user1=user2) & Q(user2=user1))
                ).first()
                if couple_relation and couple_relation.love_vow:
                    love_vow = couple_relation.love_vow
            except Exception as e:
                print(f"获取爱情誓言时出错: {str(e)}")
            
            couples_data.append({
                'user1': {
                    'id': user1.id,
                    'name': user1.name,
                    'avatar': user1_avatar
                },
                'user2': {
                    'id': user2.id,
                    'name': user2.name,
                    'avatar': user2_avatar
                },
                'total_followers': total_followers,
                'love_vow': love_vow
            })
        except Exception as e:
            print(f"处理情侣时出错: {str(e)}")
            continue
    
    # 按总粉丝数排序
    couples_data.sort(key=lambda x: x['total_followers'], reverse=True)
    
    # 取前10个
    hot_couples = couples_data[:10]
    
    return JsonResponse({'success': True, 'hot_couples': hot_couples})