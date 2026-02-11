from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, F
from django.utils import timezone
from .models import Moment, Tag, Like, Comment, CommentLike
from .serializers import MomentSerializer, TagSerializer, LikeSerializer
from user.models import Collection


class MomentViewSet(viewsets.ModelViewSet):
    """动态视图集"""
    queryset = Moment.objects.all().order_by('-created_at')
    serializer_class = MomentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """根据不同的action设置不同的权限"""
        print(f"[DEBUG] get_permissions called, action: {self.action}")
        if self.action in ['list', 'retrieve', 'hot_moments', 'hot_favorites']:
            # 查看动态列表和详情时允许匿名访问
            print(f"[DEBUG] AllowAny for action: {self.action}")
            return [AllowAny()]
        elif self.action in ['comment_like']:
            # 评论点赞需要登录
            print(f"[DEBUG] IsAuthenticated for comment_like action")
            return [IsAuthenticated()]
        else:
            # 其他操作需要登录
            print(f"[DEBUG] Default permission for action: {self.action}")
            return super().get_permissions()
    
    def list(self, request, *args, **kwargs):
        """获取动态列表，支持筛选和搜索"""
        filter_type = request.query_params.get('filter', 'latest')
        search_term = request.query_params.get('search', '')
        topic_id = request.query_params.get('topic', '')
        page = int(request.query_params.get('page', 1))
        
        # 生成缓存键
        cache_key = f'moment:list:{filter_type}:{search_term}:{topic_id}:{page}'
        cached_result = None
        
        # 尝试从缓存获取
        try:
            from django.core.cache import caches
            master_cache = caches['master_cache']
            cached_result = master_cache.get(cache_key)
            if cached_result:
                return Response(cached_result)
        except Exception as e:
            print(f"缓存读取失败: {e}")
        
        # 基础查询：只查询分享的动态
        queryset = Moment.objects.filter(is_shared=True)
        
        # 按话题筛选
        if topic_id:
            queryset = queryset.filter(tags__id=topic_id)
        
        # 搜索功能
        if search_term:
            # 搜索动态作者（用户名、昵称）和动态内容
            from django.db.models import Q
            queryset = queryset.filter(
                Q(user__username__icontains=search_term) |
                Q(user__name__icontains=search_term) |
                Q(content__icontains=search_term)
            )
        
        # 根据筛选类型构建不同的查询
        if filter_type == 'latest':
            # 最新：按创建时间倒序排列
            queryset = queryset.order_by('-created_at')
        elif filter_type == 'popular':
            # 热门：按热度分数排序
            # 先获取所有动态，计算热度分数并排序
            moments_list = list(queryset)
            moments_list.sort(key=lambda x: x.get_hot_score() if hasattr(x, 'get_hot_score') else (x.likes * 1.0 + x.comments * 0.5 + x.favorites * 0.3), reverse=True)
            # 转回查询集（这里简化处理，实际项目中可能需要更复杂的实现）
            if moments_list:
                # 保持排序顺序
                from django.db.models import Case, When
                preserved = Case(*[When(id=moment.id, then=pos) for pos, moment in enumerate(moments_list)])
                queryset = Moment.objects.filter(id__in=[m.id for m in moments_list]).order_by(preserved)
        else:  # recommended
            # 推荐：随机排序
            import random
            moments_list = list(queryset)
            random.shuffle(moments_list)
            if moments_list:
                # 保持排序顺序
                from django.db.models import Case, When
                preserved = Case(*[When(id=moment.id, then=pos) for pos, moment in enumerate(moments_list)])
                queryset = Moment.objects.filter(id__in=[m.id for m in moments_list]).order_by(preserved)
        
        # 分页处理
        page_obj = self.paginate_queryset(queryset)
        if page_obj is not None:
            serializer = self.get_serializer(page_obj, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            # 缓存结果，有效期5分钟
            try:
                from django.core.cache import caches
                master_cache = caches['master_cache']
                master_cache.set(cache_key, paginated_response.data, 300)
            except Exception as e:
                print(f"缓存写入失败: {e}")
            return paginated_response
        
        serializer = self.get_serializer(queryset, many=True)
        # 缓存结果，有效期5分钟
        try:
            from django.core.cache import caches
            master_cache = caches['master_cache']
            master_cache.set(cache_key, serializer.data, 300)
        except Exception as e:
            print(f"缓存写入失败: {e}")
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def hot_moments(self, request):
        """获取热门动态排行"""
        # 获取时间范围参数
        time_range = request.GET.get('time_range', '7days')
        
        # 生成缓存键
        cache_key = f'hot:moments:{time_range}'
        cached_result = None
        
        # 尝试从缓存获取
        try:
            from django.core.cache import caches
            master_cache = caches['master_cache']
            cached_result = master_cache.get(cache_key)
            if cached_result:
                return Response(cached_result)
        except Exception as e:
            print(f"缓存读取失败: {e}")
        
        # 根据时间范围计算起始时间
        if time_range == '7days':
            start_time = timezone.now() - timezone.timedelta(days=7)
        elif time_range == '30days':
            start_time = timezone.now() - timezone.timedelta(days=30)
        else:  # all
            start_time = timezone.datetime.min
        
        # 计算热度分数：与get_hot_score方法一致
        hot_moments = Moment.objects.filter(
            created_at__gte=start_time
        ).annotate(
            hot_score=F('likes') * 1.0 + F('comments') * 2.0 + F('favorites') * 1.5 + F('view_count') * 0.1
        ).order_by('-hot_score')[:20]  # 取前20条热门动态
        
        serializer = MomentSerializer(hot_moments, many=True)
        
        # 构建响应数据
        response_data = {
            'message': '获取热门动态成功',
            'hot_moments': serializer.data,
            'time_range': time_range
        }
        
        # 缓存结果，有效期5分钟
        try:
            from django.core.cache import caches
            master_cache = caches['master_cache']
            master_cache.set(cache_key, response_data, 300)
        except Exception as e:
            print(f"缓存写入失败: {e}")
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def hot_favorites(self, request):
        """获取热门收藏排行"""
        # 生成缓存键
        cache_key = 'hot:favorites'
        cached_result = None
        
        # 尝试从缓存获取
        try:
            from django.core.cache import caches
            master_cache = caches['master_cache']
            cached_result = master_cache.get(cache_key)
            if cached_result:
                return Response(cached_result)
        except Exception as e:
            print(f"缓存读取失败: {e}")
        
        # 按收藏数排序获取热门动态
        hot_favorites = Moment.objects.order_by('-favorites')[:20]  # 取前20条热门收藏
        
        serializer = MomentSerializer(hot_favorites, many=True)
        
        # 构建响应数据
        response_data = {
            'message': '获取热门收藏成功',
            'hot_favorites': serializer.data
        }
        
        # 缓存结果，有效期5分钟
        try:
            from django.core.cache import caches
            master_cache = caches['master_cache']
            master_cache.set(cache_key, response_data, 300)
        except Exception as e:
            print(f"缓存写入失败: {e}")
        
        return Response(response_data, status=status.HTTP_200_OK)
    
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
            
            # 清除缓存
            try:
                from django.core.cache import caches
                master_cache = caches['master_cache']
                # 清除社区动态列表缓存
                master_cache.delete_pattern('community:*')
                master_cache.delete_pattern('moment:list:*')
                # 清除用户收藏列表缓存
                user_id = request.user.id
                master_cache.delete(f'user:favorites:{user_id}')
                # 清除用户收藏页面缓存
                master_cache.delete_pattern(f'user:collections:{user_id}*')
                master_cache.delete_pattern(f'user:collections:page:{user_id}*')
                # 清除热门动态和热门收藏缓存
                master_cache.delete('hot:moments:7days')
                master_cache.delete('hot:favorites')
            except Exception as e:
                print(f"缓存清除失败: {e}")
            
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
            
            # 清除缓存
            try:
                from django.core.cache import caches
                master_cache = caches['master_cache']
                # 清除社区动态列表缓存
                master_cache.delete_pattern('community:*')
                master_cache.delete_pattern('moment:list:*')
            except Exception as e:
                print(f"缓存清除失败: {e}")
            
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
        collection, created = Collection.objects.get_or_create(
            user=request.user,
            content_type='moment',
            object_id=moment.id
        )
        
        if created:
            # 增加收藏数
            moment.favorites = F('favorites') + 1
            moment.save()
            moment.refresh_from_db()  # 刷新数据
            
            # 清除缓存
            try:
                from django.core.cache import caches
                master_cache = caches['master_cache']
                # 清除社区动态列表缓存
                master_cache.delete_pattern('community:*')
                master_cache.delete_pattern('moment:list:*')
                # 清除用户收藏列表缓存
                user_id = request.user.id
                master_cache.delete(f'user:favorites:{user_id}')
                # 清除用户收藏页面缓存
                master_cache.delete_pattern(f'user:collections:{user_id}*')
                master_cache.delete_pattern(f'user:collections:page:{user_id}*')
                # 清除热门动态和热门收藏缓存
                master_cache.delete('hot:moments:7days')
                master_cache.delete('hot:favorites')
            except Exception as e:
                print(f"缓存清除失败: {e}")
            
            return Response({
                'message': '收藏成功',
                'favorites': moment.favorites
            }, status=status.HTTP_200_OK)
        else:
            # 已收藏，取消收藏
            collection.delete()
            # 减少收藏数
            moment.favorites = F('favorites') - 1
            moment.save()
            moment.refresh_from_db()  # 刷新数据
            
            # 清除缓存
            try:
                from django.core.cache import caches
                master_cache = caches['master_cache']
                # 清除社区动态列表缓存
                master_cache.delete_pattern('community:*')
                master_cache.delete_pattern('moment:list:*')
                # 清除用户收藏列表缓存
                user_id = request.user.id
                master_cache.delete(f'user:favorites:{user_id}')
                # 清除用户收藏页面缓存
                master_cache.delete_pattern(f'user:collections:{user_id}*')
                master_cache.delete_pattern(f'user:collections:page:{user_id}*')
                # 清除热门动态和热门收藏缓存
                master_cache.delete('hot:moments:7days')
                master_cache.delete('hot:favorites')
            except Exception as e:
                print(f"缓存清除失败: {e}")
            
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
        is_favorited = Collection.objects.filter(user=request.user, content_type='moment', object_id=moment.id).exists()
        return Response({'is_favorited': is_favorited}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def user_favorites(self, request):
        """获取当前用户收藏的动态"""
        # 生成缓存键
        user_id = request.user.id
        cache_key = f'user:favorites:{user_id}'
        cached_result = None
        
        print(f"[DEBUG] 调用 user_favorites 方法，用户ID: {user_id}, 缓存键: {cache_key}")
        
        # 尝试从缓存获取
        try:
            from django.core.cache import caches
            master_cache = caches['master_cache']
            print(f"[DEBUG] 尝试从缓存获取数据，缓存后端: master_cache")
            cached_result = master_cache.get(cache_key)
            if cached_result:
                print(f"[DEBUG] 缓存命中，返回缓存数据")
                return Response(cached_result)
            else:
                print(f"[DEBUG] 缓存未命中，从数据库查询")
        except Exception as e:
            print(f"[ERROR] 缓存读取失败: {e}")
        
        # 从数据库查询
        print(f"[DEBUG] 从数据库查询收藏动态")
        user_collections = Collection.objects.filter(user=request.user, content_type='moment').order_by('-created_at')
        moment_ids = [collection.object_id for collection in user_collections]
        moments = Moment.objects.filter(id__in=moment_ids).order_by('-created_at')
        print(f"[DEBUG] 查询到 {len(moments)} 条收藏动态")
        serializer = MomentSerializer(moments, many=True)
        
        # 构建响应数据
        response_data = {
            'message': '获取收藏动态成功',
            'favorites': serializer.data
        }
        
        # 缓存结果，有效期5分钟
        try:
            from django.core.cache import caches
            master_cache = caches['master_cache']
            print(f"[DEBUG] 尝试写入缓存，缓存键: {cache_key}, 有效期: 300秒")
            result = master_cache.set(cache_key, response_data, 300)
            print(f"[DEBUG] 缓存写入结果: {result}")
        except Exception as e:
            print(f"[ERROR] 缓存写入失败: {e}")
        
        print(f"[DEBUG] 返回响应数据")
        return Response(response_data, status=status.HTTP_200_OK)
    
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
        
        # 清除缓存
        try:
            from django.core.cache import caches
            master_cache = caches['master_cache']
            # 清除社区动态列表缓存
            master_cache.delete_pattern('community:*')
            master_cache.delete_pattern('moment:list:*')
        except Exception as e:
            print(f"缓存清除失败: {e}")
        
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
                    'likes': comment.likes,
                    'is_author': True,
                    'replies': []
                }
            }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """获取动态的评论列表"""
        moment = self.get_object()
        # 只获取一级评论（parent_id 为 null 的评论）
        comments = moment.comment_set.filter(parent_id__isnull=True)
        
        comments_list = []
        for comment in comments:
            # 获取该评论的二级回复
            replies = comment.replies.all()
            replies_list = []
            for reply in replies:
                replies_list.append({
                    'id': reply.id,
                    'user': reply.user.name,
                    'avatar': reply.user.profile.userAvatar.url,
                    'content': reply.content,
                    'created_at': reply.created_at,
                    'is_author': reply.user == request.user,
                    'likes': reply.likes,
                    'is_liked': CommentLike.objects.filter(user=request.user, comment=reply).exists() if request.user.is_authenticated else False
                })
            
            comments_list.append({
                'id': comment.id,
                'user': comment.user.name,
                'avatar': comment.user.profile.userAvatar.url,
                'content': comment.content,
                'created_at': comment.created_at,
                'parent_id': comment.parent_id,
                'is_author': comment.user == request.user,
                'likes': comment.likes,
                'is_liked': CommentLike.objects.filter(user=request.user, comment=comment).exists() if request.user.is_authenticated else False,
                'replies': replies_list
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
            
            # 清除相关缓存
            try:
                from django.core.cache import caches
                master_cache = caches['master_cache']
                # 清除社区动态列表缓存
                master_cache.delete_pattern('community:*')
                master_cache.delete_pattern('moment:list:*')
                # 清除动态详情缓存
                master_cache.delete(f'moment:detail:{pk}')
            except Exception as e:
                print(f"缓存清除失败: {e}")
            
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
    
    @action(detail=True, methods=['post'], url_path='comment/(?P<comment_id>\d+)/like')
    def comment_like(self, request, pk=None, comment_id=None):
        """点赞评论"""
        print(f"[DEBUG] 评论点赞请求 - 方法: {request.method}, 用户: {request.user}, moment_id: {pk}, comment_id: {comment_id}")
        print(f"[DEBUG] 请求头: {dict(request.headers)}")
        print(f"[DEBUG] 请求体: {request.body}")
        
        # 检查请求方法
        if request.method != 'POST':
            print(f"[ERROR] 错误的请求方法: {request.method}")
            return Response({
                'message': f'方法 "{request.method}" 不被允许。'
            }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
        moment = self.get_object()
        
        try:
            comment = Comment.objects.get(id=comment_id, moment=moment)
            
            # 检查是否已经点赞
            like, created = CommentLike.objects.get_or_create(user=request.user, comment=comment)
            
            if created:
                # 增加点赞数
                comment.likes = F('likes') + 1
                comment.save()
                comment.refresh_from_db()  # 刷新数据
                
                # 清除相关缓存
                try:
                    from django.core.cache import caches
                    master_cache = caches['master_cache']
                    # 清除社区动态列表缓存
                    master_cache.delete_pattern('community:*')
                    master_cache.delete_pattern('moment:list:*')
                    # 清除动态详情缓存
                    master_cache.delete(f'moment:detail:{pk}')
                except Exception as e:
                    print(f"缓存清除失败: {e}")
                
                return Response({
                    'message': '点赞成功',
                    'likes': comment.likes,
                    'is_liked': True
                }, status=status.HTTP_200_OK)
            else:
                # 已点赞，取消点赞
                like.delete()
                # 减少点赞数
                comment.likes = F('likes') - 1 if comment.likes > 0 else 0
                comment.save()
                comment.refresh_from_db()  # 刷新数据
                
                # 清除相关缓存
                try:
                    from django.core.cache import caches
                    master_cache = caches['master_cache']
                    # 清除社区动态列表缓存
                    master_cache.delete_pattern('community:*')
                    master_cache.delete_pattern('moment:list:*')
                    # 清除动态详情缓存
                    master_cache.delete(f'moment:detail:{pk}')
                except Exception as e:
                    print(f"缓存清除失败: {e}")
                
                return Response({
                    'message': '取消点赞成功',
                    'likes': comment.likes,
                    'is_liked': False
                }, status=status.HTTP_200_OK)
                
        except Comment.DoesNotExist:
            return Response({
                'message': '评论不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'message': f'点赞失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TagViewSet(viewsets.ModelViewSet):
    """标签视图集"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """根据不同的action设置不同的权限"""
        if self.action == 'trending_tags':
            # 热门标签接口允许匿名访问
            return [AllowAny()]
        else:
            # 其他操作需要登录
            return super().get_permissions()
    
    @action(detail=False, methods=['get'])
    def trending_tags(self, request):
        """获取热门标签"""
        # 统计标签使用次数，取前20个热门标签
        trending_tags = Tag.objects.annotate(
            usage_count=Count('moments')
        ).order_by('-usage_count')[:20]
        
        serializer = TagSerializer(trending_tags, many=True)
        return Response({
            'success': True,
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
            custom_tags = request.POST.get('custom_tags', '')
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
                
                # 处理自定义标签
                if custom_tags:
                    # 分割自定义标签（使用空格分隔）
                    custom_tags_list = custom_tags.split()
                    for tag_name in custom_tags_list:
                        tag_name = tag_name.strip()
                        # 移除#符号
                        tag_name = tag_name.replace('#', '')
                        if tag_name:
                            tag, created = Tag.objects.get_or_create(name=tag_name)
                            moment.tags.add(tag)
            
                # 处理图片
                for image in images:
                    MomentImage.objects.create(moment=moment, image=image)
                
                # 清除相关缓存，确保社区页面能及时显示新动态
                try:
                    from django.core.cache import caches
                    master_cache = caches['master_cache']
                    # 清除社区页面缓存
                    master_cache.delete('community:latest:1')
                    # 清除热门动态缓存
                    master_cache.delete_pattern('hot:moments:*')
                except Exception as e:
                    print(f"清除缓存失败: {e}")
                
                messages.success(request, '动态发布成功')
                return redirect('moments')
            except Exception as e:
                messages.error(request, f'发布失败: {str(e)}')
                return redirect('moments')
    
    # 获取粉丝数和关注数
    from user.models import Follow
    followers_count = Follow.objects.filter(following=request.user, is_deleted=False).count()
    following_count = Follow.objects.filter(follower=request.user, is_deleted=False).count()
    
    return render(request, 'moments.html', {
        'moments': moments,
        'user': request.user,
        'followers_count': followers_count,
        'following_count': following_count
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
        
        # 清除相关缓存
        try:
            from django.core.cache import caches
            master_cache = caches['master_cache']
            # 清除动态列表缓存
            master_cache.delete_pattern('moment:list:*')
            # 清除热门动态缓存
            master_cache.delete_pattern('hot:moments:*')
            # 清除热门收藏缓存
            master_cache.delete('hot:favorites')
            # 清除社区页面缓存
            master_cache.delete_pattern('community:*')
        except Exception as cache_error:
            print(f"缓存清除失败: {cache_error}")
        
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
        
        # 清除相关缓存
        try:
            from django.core.cache import caches
            master_cache = caches['master_cache']
            # 清除动态列表缓存
            master_cache.delete_pattern('moment:list:*')
            # 清除热门动态缓存
            master_cache.delete_pattern('hot:moments:*')
            # 清除热门收藏缓存
            master_cache.delete('hot:favorites')
            # 清除社区页面缓存
            master_cache.delete_pattern('community:*')
        except Exception as cache_error:
            print(f"缓存清除失败: {cache_error}")
        
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
        
        # 清除相关缓存
        try:
            from django.core.cache import caches
            master_cache = caches['master_cache']
            # 清除动态列表缓存
            master_cache.delete_pattern('moment:list:*')
            # 清除热门动态缓存
            master_cache.delete_pattern('hot:moments:*')
            # 清除热门收藏缓存
            master_cache.delete('hot:favorites')
            # 清除社区页面缓存
            master_cache.delete_pattern('community:*')
        except Exception as cache_error:
            print(f"缓存清除失败: {cache_error}")
        
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
        # 如果7天内没有数据，自动使用30天
        if not moments.exists():
            current_time_range = '30days'
            start_date = timezone.now() - timezone.timedelta(days=30)
            moments = Moment.objects.filter(is_shared=True, created_at__gte=start_date)
            # 如果30天内也没有数据，使用全部
            if not moments.exists():
                current_time_range = 'all'
                moments = Moment.objects.filter(is_shared=True)
    elif current_time_range == '30days':
        start_date = timezone.now() - timezone.timedelta(days=30)
        moments = moments.filter(created_at__gte=start_date)
        # 如果30天内没有数据，使用全部
        if not moments.exists():
            current_time_range = 'all'
            moments = Moment.objects.filter(is_shared=True)
    # 'all' 不需要时间筛选
    
    # 按热度值排序
    # 先获取所有动态，然后计算热度值并排序
    moments_list = list(moments)
    moments_list.sort(key=lambda x: x.get_hot_score(), reverse=True)
    
    # 限制前50条
    hot_posts_with_rank = []
    for idx, post in enumerate(moments_list[:10]):
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
    filter_type = request.GET.get('filter', 'latest')  # 默认为最新
    
    # 生成缓存键
    cache_key = f'community:{filter_type}:{page}'
    cached_result = None
    
    # 尝试从缓存获取
    try:
        from django.core.cache import caches
        master_cache = caches['master_cache']
        cached_result = master_cache.get(cache_key)
        if cached_result:
            return JsonResponse(cached_result)
    except Exception as e:
        print(f"缓存读取失败: {e}")
    
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 基础查询：只查询分享的动态
    base_query = Moment.objects.filter(is_shared=True)
    
    # 根据筛选类型构建不同的查询
    if filter_type == 'latest':
        # 最新：按创建时间倒序排列
        moments = base_query.order_by('-created_at')[offset:offset + page_size]
        total_count = base_query.count()
    elif filter_type == 'popular':
        # 热门：按热度分数排序
        # 先获取所有动态，计算热度分数并排序
        moments_list = list(base_query)
        moments_list.sort(key=lambda x: x.get_hot_score() if hasattr(x, 'get_hot_score') else (x.likes * 1.0 + x.comments * 0.5), reverse=True)
        # 分页
        moments = moments_list[offset:offset + page_size]
        total_count = len(moments_list)
    else:  # recommended
        # 推荐：暂时使用最新的逻辑，后续可根据用户兴趣进行个性化推荐
        moments = base_query.order_by('-created_at')[offset:offset + page_size]
        total_count = base_query.count()
    
    # 序列化数据
    moments_data = []
    for moment in moments:
        # 获取用户头像
        avatar_url = moment.user.profile.userAvatar.url if hasattr(moment.user, 'profile') and hasattr(moment.user.profile, 'userAvatar') and moment.user.profile.userAvatar else ''
        
        # 获取动态图片
        image_urls = []
        if hasattr(moment, 'moment_images'):
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
            'comments': moment.comments,
            'view_count': moment.view_count
        })
    
    # 检查是否还有更多数据
    has_more = total_count > offset + page_size
    
    # 构建响应数据
    response_data = {
        'success': True,
        'moments': moments_data,
        'has_more': has_more,
        'page': page,
        'page_size': page_size
    }
    
    # 缓存结果，有效期5分钟
    try:
        from django.core.cache import caches
        master_cache = caches['master_cache']
        master_cache.set(cache_key, response_data, 300)
    except Exception as e:
        print(f"缓存写入失败: {e}")
    
    return JsonResponse(response_data)
