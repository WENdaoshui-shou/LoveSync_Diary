from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from .models import OfficialColumn, ColumnArticle, ColumnComment, ArticleLike, ColumnSubscription
from .serializers import (
    OfficialColumnSerializer, ColumnArticleSerializer,
    ColumnCommentSerializer, ColumnSubscriptionSerializer
)

# Web Views (for rendering templates)



def column_detail_view(request, column_slug):
    """专栏详情页面"""
    column = get_object_or_404(OfficialColumn, slug=column_slug, is_active=True)
    articles = ColumnArticle.objects.filter(column=column).order_by('id')
    
    # 获取当前用户是否订阅
    if request.user.is_authenticated:
        try:
            subscription = ColumnSubscription.objects.get(user=request.user, column=column)
            column.is_subscribed = subscription.is_subscribed
        except ColumnSubscription.DoesNotExist:
            column.is_subscribed = False
    else:
        column.is_subscribed = False
    
    return render(request, 'articles/column_detail.html', {
        'column': column,
        'articles': articles
    })


def article_detail_view(request, article_id):
    """文章详情页面"""
    article = get_object_or_404(ColumnArticle, id=article_id)
    # 增加浏览量
    article.view_count += 1
    article.save()
    
    # 获取相关推荐
    related_articles = ColumnArticle.objects.filter(
        column=article.column
    ).exclude(id=article.id)[:3]
    
    # 获取当前用户是否点赞
    if request.user.is_authenticated:
        article.is_liked = ArticleLike.objects.filter(
            article=article,
            user=request.user
        ).exists()
    else:
        article.is_liked = False
    
    # 获取内容类型ID
    from django.contrib.contenttypes.models import ContentType
    content_type = ContentType.objects.get_for_model(ColumnArticle)
    content_type_id = content_type.id
    
    return render(request, 'articles/article_detail.html', {
        'article': article,
        'related_articles': related_articles,
        'content_type_id': content_type_id
    })

def articles_view(request):
    """文章列表页面"""
    articles = ColumnArticle.objects.all().order_by('-published_at')
    
    # 获取所有专栏
    columns = OfficialColumn.objects.filter(is_active=True).order_by('id')
    
    return render(request, 'articles/articles.html', {
        'articles': articles,
        'columns': columns
    })


class OfficialColumnViewSet(viewsets.ModelViewSet):
    """官方专栏视图集"""
    queryset = OfficialColumn.objects.filter(is_active=True)
    serializer_class = OfficialColumnSerializer
    permission_classes = [AllowAny]
    
    def get_serializer_context(self):
        """获取序列化器上下文"""
        context = super().get_serializer_context()
        if self.request.user.is_authenticated:
            context['user'] = self.request.user
        return context
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        """订阅/取消订阅专栏"""
        column = self.get_object()
        user = request.user
        
        subscription, created = ColumnSubscription.objects.get_or_create(
            user=user,
            column=column
        )
        
        # 切换订阅状态
        subscription.is_subscribed = not subscription.is_subscribed
        subscription.save()
        
        # 更新订阅人数
        active_subscribers = ColumnSubscription.objects.filter(
            column=column,
            is_subscribed=True
        ).count()
        column.subscriber_count = active_subscribers
        column.save()
        
        # 发送系统通知
        if subscription.is_subscribed:
            # 订阅成功通知
            pass  # 集成现有消息模块
        
        return Response({
            'is_subscribed': subscription.is_subscribed,
            'subscriber_count': column.subscriber_count
        })
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """按分类获取专栏"""
        category = request.query_params.get('category', 'all')
        queryset = self.queryset
        
        if category != 'all':
            queryset = queryset.filter(category=category)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ColumnArticleViewSet(viewsets.ModelViewSet):
    """专栏文章视图集"""
    queryset = ColumnArticle.objects.all()
    serializer_class = ColumnArticleSerializer
    permission_classes = [AllowAny]
    
    def get_serializer_context(self):
        """获取序列化器上下文"""
        context = super().get_serializer_context()
        if self.request.user.is_authenticated:
            context['user'] = self.request.user
        return context
    
    def retrieve(self, request, *args, **kwargs):
        """获取文章详情，增加浏览量"""
        instance = self.get_object()
        instance.view_count += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_column(self, request):
        """按专栏获取文章"""
        column_id = request.query_params.get('column_id')
        if not column_id:
            return Response({'error': 'column_id is required'}, status=400)
        
        queryset = self.queryset.filter(column_id=column_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def infinite_load(self, request):
        """无限加载文章"""
        page = int(request.query_params.get('page', 1))
        page_size = 10
        offset = (page - 1) * page_size
        
        category = request.query_params.get('category', 'all')
        queryset = self.queryset
        
        if category != 'all':
            queryset = queryset.filter(column__category=category)
        
        articles = queryset.order_by('-published_at')[offset:offset + page_size]
        serializer = self.get_serializer(articles, many=True)
        
        has_more = queryset.count() > offset + page_size
        
        return Response({
            'articles': serializer.data,
            'has_more': has_more,
            'page': page
        })

class ColumnCommentViewSet(viewsets.ModelViewSet):
    """专栏评论视图集"""
    queryset = ColumnComment.objects.all()
    serializer_class = ColumnCommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_context(self):
        """获取序列化器上下文"""
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context
    
    def perform_create(self, serializer):
        """创建评论"""
        comment = serializer.save(user=self.request.user)
        
        # 更新文章评论数
        article = comment.article
        article.comment_count = article.comments.count()
        article.save()
    
    @action(detail=False, methods=['get'])
    def by_article(self, request):
        """按文章获取评论"""
        article_id = request.query_params.get('article_id')
        if not article_id:
            return Response({'error': 'article_id is required'}, status=400)
        
        queryset = self.queryset.filter(article_id=article_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def infinite_load(self, request):
        """无限加载评论"""
        article_id = request.query_params.get('article_id')
        if not article_id:
            return Response({'error': 'article_id is required'}, status=400)
        
        page = int(request.query_params.get('page', 1))
        page_size = 20
        offset = (page - 1) * page_size
        
        queryset = self.queryset.filter(article_id=article_id)
        comments = queryset.order_by('-created_at')[offset:offset + page_size]
        serializer = self.get_serializer(comments, many=True)
        
        has_more = queryset.count() > offset + page_size
        
        return Response({
            'comments': serializer.data,
            'has_more': has_more,
            'page': page
        })

class ArticleLikeViewSet(viewsets.ModelViewSet):
    """文章点赞视图集"""
    queryset = ArticleLike.objects.all()
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def toggle_like(self, request):
        """切换点赞状态"""
        article_id = request.data.get('article_id')
        user = request.user
        
        if not article_id:
            return Response({'error': 'article_id is required'}, status=400)
        
        try:
            article = ColumnArticle.objects.get(id=article_id)
        except ColumnArticle.DoesNotExist:
            return Response({'error': 'Article not found'}, status=404)
        
        # 查找现有点赞
        like, created = ArticleLike.objects.get_or_create(
            article=article,
            user=user
        )
        
        if not created:
            # 已点赞，取消点赞
            like.delete()
            is_liked = False
        else:
            # 未点赞，添加点赞
            is_liked = True
        
        # 点赞数会通过信号自动更新，这里重新获取
        article.refresh_from_db()
        
        return Response({
            'is_liked': is_liked,
            'like_count': article.like_count
        })
