from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, F
from django.utils import timezone
from .models import Moment, Tag, Like, Favorite, Comment
from .serializers import MomentSerializer, TagSerializer, LikeSerializer, FavoriteSerializer


class MomentViewSet(viewsets.ModelViewSet):
    """动态视图集"""
    queryset = Moment.objects.all().order_by('-created_at')
    serializer_class = MomentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """根据不同的action设置不同的权限"""
        if self.action in ['list', 'retrieve', 'hot_moments', 'hot_favorites']:
            # 查看动态列表和详情时允许匿名访问
            return [AllowAny()]
        else:
            # 其他操作需要登录
            return super().get_permissions()
    
    @action(detail=False, methods=['get'])
    def hot_moments(self, request):
        """获取热门动态排行"""
        # 计算热度分数：点赞数 * 1.0 + 评论数 * 0.5 + 收藏数 * 0.8
        # 只显示最近7天的动态
        one_week_ago = timezone.now() - timezone.timedelta(days=7)
        
        hot_moments = Moment.objects.filter(
            created_at__gte=one_week_ago
        ).annotate(
            hot_score=F('likes') * 1.0 + F('comments') * 0.5 + F('favorites') * 0.8
        ).order_by('-hot_score')[:20]  # 取前20条热门动态
        
        serializer = MomentSerializer(hot_moments, many=True)
        return Response({
            'message': '获取热门动态成功',
            'hot_moments': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def hot_favorites(self, request):
        """获取热门收藏排行"""
        # 按收藏数排序获取热门动态
        hot_favorites = Moment.objects.order_by('-favorites')[:20]  # 取前20条热门收藏
        
        serializer = MomentSerializer(hot_favorites, many=True)
        return Response({
            'message': '获取热门收藏成功',
            'hot_favorites': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """点赞动态"""
        moment = self.get_object()
        
        # 检查是否已经点赞
        like, created = Like.objects.get_or_create(user=request.user, moment=moment)
        
        if created:
            # 增加点赞数
            moment.likes = F('likes') + 1
            moment.save()
            moment.refresh_from_db()  # 刷新数据
            
            return Response({
                'message': '点赞成功',
                'likes': moment.likes,
                'is_liked': True
            }, status=status.HTTP_200_OK)
        else:
            # 已点赞，取消点赞
            like.delete()
            # 减少点赞数
            moment.likes = F('likes') - 1
            moment.save()
            moment.refresh_from_db()  # 刷新数据
            
            return Response({
                'message': '取消点赞成功',
                'likes': moment.likes,
                'is_liked': False
            }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        """收藏动态"""
        moment = self.get_object()
        
        # 检查是否已经收藏
        favorite, created = Favorite.objects.get_or_create(user=request.user, moment=moment)
        
        if created:
            # 增加收藏数
            moment.favorites = F('favorites') + 1
            moment.save()
            moment.refresh_from_db()  # 刷新数据
            
            return Response({
                'message': '收藏成功',
                'favorites': moment.favorites
            }, status=status.HTTP_200_OK)
        else:
            # 已收藏，取消收藏
            favorite.delete()
            # 减少收藏数
            moment.favorites = F('favorites') - 1
            moment.save()
            moment.refresh_from_db()  # 刷新数据
            
            return Response({
                'message': '取消收藏成功',
                'favorites': moment.favorites
            }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def is_liked(self, request, pk=None):
        """检查当前用户是否已点赞该动态"""
        moment = self.get_object()
        is_liked = Like.objects.filter(user=request.user, moment=moment).exists()
        return Response({'is_liked': is_liked}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def is_favorited(self, request, pk=None):
        """检查当前用户是否已收藏该动态"""
        moment = self.get_object()
        is_favorited = Favorite.objects.filter(user=request.user, moment=moment).exists()
        return Response({'is_favorited': is_favorited}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def user_favorites(self, request):
        """获取当前用户收藏的动态"""
        user_favorites = Favorite.objects.filter(user=request.user).order_by('-created_at')
        moments = [fav.moment for fav in user_favorites]
        serializer = MomentSerializer(moments, many=True)
        return Response({
            'message': '获取收藏动态成功',
            'favorites': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        """添加评论"""
        moment = self.get_object()
        content = request.data.get('content')
        parent_id = request.data.get('parent_id')
        
        if not content:
            return Response({'message': '评论内容不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        comment = Comment.objects.create(
            moment=moment,
            user=request.user,
            content=content,
            parent_id=parent_id
        )
        
        # 增加评论数
        moment.comments = F('comments') + 1
        moment.save()
        moment.refresh_from_db()  # 刷新数据
        
        return Response({
                'message': '评论成功',
                'comments': moment.comments,
                'comment': {
                    'id': comment.id,
                    'user': comment.user.name,
                    'avatar': comment.user.profile.userAvatar.url if comment.user.profile.userAvatar else '',
                    'content': comment.content,
                    'created_at': comment.created_at,
                    'parent_id': comment.parent_id,
                    'replies': []
                }
            }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """获取动态的评论列表"""
        moment = self.get_object()
        comments = moment.comment_set.all()
        
        comments_list = []
        for comment in comments:
            comments_list.append({
                'id': comment.id,
                'user': comment.user.name,
                'avatar': comment.user.profile.userAvatar.url,
                'content': comment.content,
                'created_at': comment.created_at,
                'parent_id': comment.parent_id,
                'is_author': comment.user == request.user,
                'replies': [{
                    'id': reply.id,
                    'user': reply.user.name,
                    'avatar': reply.user.profile.userAvatar.url,
                    'content': reply.content,
                    'created_at': reply.created_at,
                    'is_author': reply.user == request.user
                } for reply in comment.replies.all()]
            })
        
        return Response({
            'comments': comments_list,
            'total_comments': len(comments_list)
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['delete'], url_path='delete_comment/(?P<comment_id>\d+)')
    def delete_comment(self, request, pk=None, comment_id=None):
        """删除评论"""
        moment = self.get_object()
        
        try:
            comment = Comment.objects.get(id=comment_id, moment=moment)
            
            # 检查评论是否属于当前用户
            if comment.user != request.user:
                return Response({
                    'message': '无权限删除该评论'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # 级联删除二级回复
            if comment.parent_id is None:  # 判定为主评论
                Comment.objects.filter(parent_id=comment.id, moment=moment).delete()
            
            # 删除评论
            comment.delete()
            
            # 统计所有评论（含一级+二级）
            total_comments = Comment.objects.filter(moment=moment).count()
            moment.comments = total_comments
            moment.save()
            moment.refresh_from_db()  # 刷新数据
            
            return Response({
                'message': '评论删除成功',
                'comments': moment.comments  # 返回所有评论数
            }, status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response({
                'message': '评论不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'message': f'删除评论失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TagViewSet(viewsets.ModelViewSet):
    """标签视图集"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def trending_tags(self, request):
        """获取热门标签"""
        # 统计标签使用次数，取前20个热门标签
        trending_tags = Tag.objects.annotate(
            usage_count=Count('moments')
        ).order_by('-usage_count')[:20]
        
        serializer = TagSerializer(trending_tags, many=True)
        return Response({
            'message': '获取热门标签成功',
            'trending_tags': serializer.data
        }, status=status.HTTP_200_OK)


class LikeViewSet(viewsets.ModelViewSet):
    """点赞视图集"""
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """只返回当前用户的点赞记录"""
        return self.queryset.filter(user=self.request.user)


class FavoriteViewSet(viewsets.ModelViewSet):
    """收藏视图集"""
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """只返回当前用户的收藏记录"""
        return self.queryset.filter(user=self.request.user)


# 社区视图（Web）
@login_required
def community_view(request):
    """社区页面"""
    # 获取所有分享的动态，按时间倒序排列，限制初始加载数量为10条
    moments = Moment.objects.filter(is_shared=True).order_by('-created_at')[:10]
    
    # 获取未读消息计数
    try:
        from message.models import Message, PrivateChat
        
        # 计算系统消息未读数
        unread_system_messages = Message.objects.filter(user=request.user, type='system', is_read=False).count()
        
        # 计算业务提醒未读数
        unread_business_messages = Message.objects.filter(user=request.user, type='business', is_read=False).count()
        
        # 计算私信未读数
        unread_private_chats = PrivateChat.objects.filter(recipient=request.user, message__is_read=False).count()
        
        # 总未读消息数
        total_unread_messages = unread_system_messages + unread_business_messages + unread_private_chats
    except Exception as e:
        print(f"Error calculating unread messages: {e}")
        total_unread_messages = 0
    
    return render(request, 'community.html', {
        'moments': moments,
        'user': request.user,
        'unread_message_count': total_unread_messages
    })


# 动态视图（Web）
@login_required
def moments_view(request):
    """动态页面，处理动态发布"""
    from moment.models import MomentImage, Tag
    
    # 获取当前用户的所有动态
    moments = Moment.objects.filter(user=request.user).order_by('-created_at')
    
    if request.method == 'POST':
        # 处理动态发布
        content = request.POST.get('content', '').strip()
        tags_data = request.POST.getlist('tags', [])
        images = request.FILES.getlist('image')
        
        # 验证内容
        if not content:
            messages.error(request, '动态内容不能为空')
            return redirect('moments')
        
        try:
            # 创建动态
            moment = Moment.objects.create(
                user=request.user,
                content=content
            )
            
            # 处理标签
            for tag_name in tags_data:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                moment.tags.add(tag)
            
            # 处理图片
            for image in images:
                MomentImage.objects.create(moment=moment, image=image)
            
            messages.success(request, '动态发布成功')
            return redirect('moments')
        except Exception as e:
            messages.error(request, f'发布失败: {str(e)}')
            return redirect('moments')
    
    return render(request, 'moments.html', {
        'moments': moments,
        'user': request.user
    })


# 热门动态视图（Web）
@login_required
def hot_moments_view(request):
    """热门动态页面"""
    # 计算热度分数：点赞数 * 1.0 + 评论数 * 0.5 + 收藏数 * 0.8
    # 只显示最近7天的动态
    one_week_ago = timezone.now() - timezone.timedelta(days=30)
    
    hot_moments = Moment.objects.filter(
        created_at__gte=one_week_ago,
        is_shared=True
    ).annotate(
        hot_score=F('likes') * 1.0 + F('comments') * 0.5 + F('favorites') * 0.8
    ).order_by('-hot_score')[:20]  # 取前20条热门动态
    
    # 获取热门标签
    trending_tags = Tag.objects.annotate(
        usage_count=Count('moments')
    ).order_by('-usage_count')[:10]
    
    context = {
        'hot_moments': hot_moments,
        'trending_tags': trending_tags
    }
    
    return render(request, 'hot_moments.html', context)


# 收藏动态视图（Web）



# 分享动态视图
@login_required
def share_moment(request, moment_id):
    """分享动态到社区"""
    from django.http import JsonResponse
    from moment.models import Moment
    
    try:
        moment = Moment.objects.get(id=moment_id, user=request.user)
        moment.is_shared = True
        moment.save()
        return JsonResponse({'success': True, 'message': '动态分享成功'})
    except Moment.DoesNotExist:
        return JsonResponse({'success': False, 'message': '动态不存在或无权操作'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


# 删除动态视图
@login_required
def delete_moment(request, moment_id):
    """删除动态"""
    from django.http import JsonResponse
    from moment.models import Moment
    
    try:
        moment = Moment.objects.get(id=moment_id, user=request.user)
        moment.delete()
        return JsonResponse({'success': True, 'message': '动态删除成功'})
    except Moment.DoesNotExist:
        return JsonResponse({'success': False, 'message': '动态不存在或无权操作'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


# 取消分享动态视图
@login_required
def unshare_moment(request, moment_id):
    """取消分享动态"""
    from django.http import JsonResponse
    from moment.models import Moment
    
    try:
        moment = Moment.objects.get(id=moment_id, user=request.user)
        moment.is_shared = False
        moment.save()
        return JsonResponse({'success': True, 'message': '取消分享成功'})
    except Moment.DoesNotExist:
        return JsonResponse({'success': False, 'message': '动态不存在或无权操作'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


# 热门动态排行榜视图
@login_required
def hot_ranking(request):
    """热门动态排行榜页面"""
    from django.utils import timezone
    
    # 获取时间范围参数
    current_time_range = request.GET.get('time_range', '7days')
    time_ranges = ['7days', '30days', 'all']
    
    # 构建查询
    moments = Moment.objects.filter(is_shared=True)
    
    # 时间筛选
    if current_time_range == '7days':
        start_date = timezone.now() - timezone.timedelta(days=7)
        moments = moments.filter(created_at__gte=start_date)
    elif current_time_range == '30days':
        start_date = timezone.now() - timezone.timedelta(days=30)
        moments = moments.filter(created_at__gte=start_date)
    
    # 按热度值排序
    # 先获取所有动态，然后计算热度值并排序
    moments_list = list(moments)
    moments_list.sort(key=lambda x: x.get_hot_score(), reverse=True)
    
    # 限制前50条
    hot_posts_with_rank = []
    for idx, post in enumerate(moments_list[:50]):
        rank = idx + 1  # 排名从1开始
        rank_times_100 = rank * 100  # 提前计算rank*100
        hot_posts_with_rank.append({
            'post': post,
            'rank': rank,
            'rank_times_100': rank_times_100,  # 把计算结果传给模板
        })
    
    context = {
        'page_title': '热门动态排行榜',
        'hot_posts_with_rank': hot_posts_with_rank,
        'current_time_range': current_time_range,
        'time_ranges': time_ranges
    }
    
    return render(request, 'community/hot_ranking.html', context)


# 动态分享页面视图（无需登录即可访问）
def moment_share_view(request, moment_id):
    """动态分享页面视图"""
    from django.shortcuts import render
    from .models import Moment
    from django.db.models import F
    
    try:
        # 查询动态数据
        moment = Moment.objects.get(id=moment_id)
        
        # 浏览数+1（使用F表达式避免并发问题）
        moment.view_count = F('view_count') + 1
        moment.save()
        moment.refresh_from_db()  # 刷新数据
        
        # 传递完整的动态信息到模板
        context = {
            'moment': moment,
            'user': moment.user,
            'meta_title': f"{moment.user.username}的动态分享",
            'meta_description': f"{moment.content[:100]}..." if len(moment.content) > 100 else moment.content
        }
        
        return render(request, 'moment_share.html', context)
    except Moment.DoesNotExist:
        # 动态不存在时返回友好提示
        return render(request, 'moment_share.html', {
            'error': '动态不存在',
            'meta_title': '动态不存在',
            'meta_description': '您访问的动态不存在或已被删除'
        })
    except Exception as e:
        # 其他错误时返回友好提示
        return render(request, 'moment_share.html', {
            'error': '访问出错',
            'meta_title': '访问出错',
            'meta_description': '访问动态时出现错误'
        })


# 社区动态分页加载API
from django.http import JsonResponse
def load_more_moments(request):
    """加载更多社区动态的API"""
    page = int(request.GET.get('page', 1))
    page_size = 10
    
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 查询分享的动态，按时间倒序排列，支持分页
    moments = Moment.objects.filter(is_shared=True).order_by('-created_at')[offset:offset + page_size]
    
    # 序列化数据
    moments_data = []
    for moment in moments:
        # 获取用户头像
        avatar_url = moment.user.profile.userAvatar.url if moment.user.profile.userAvatar else ''
        
        # 获取动态图片
        image_urls = []
        for image in moment.moment_images.all():
            image_urls.append(image.image.url)
        
        # 获取VIP信息
        vip_info = {}
        if hasattr(moment.user, 'vip'):
            vip_info['is_active'] = moment.user.vip.is_active
            vip_info['level'] = moment.user.vip.level
            vip_info['level_display'] = moment.user.vip.get_level_display()
            vip_info['level_color'] = moment.user.vip.get_level_color()
            vip_info['level_text_color'] = moment.user.vip.get_level_text_color()
        
        moments_data.append({
            'id': moment.id,
            'user': {
                'id': moment.user.id,
                'username': moment.user.username,
                'name': moment.user.name,
                'avatar': avatar_url,
                'vip': vip_info
            },
            'content': moment.content,
            'images': image_urls,
            'created_at': moment.created_at.strftime('%Y-%m-%d %H:%M'),
            'likes': moment.likes,
            'comments': moment.comments
        })
    
    # 检查是否还有更多数据
    has_more = Moment.objects.filter(is_shared=True).count() > offset + page_size
    
    return JsonResponse({
        'success': True,
        'moments': moments_data,
        'has_more': has_more,
        'page': page,
        'page_size': page_size
    })
