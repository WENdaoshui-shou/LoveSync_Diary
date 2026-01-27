from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.utils import timezone
from .models import CommunityEvent
from .serializers import CommunityEventSerializer


class CommunityEventViewSet(viewsets.ModelViewSet):
    queryset = CommunityEvent.objects.all()
    serializer_class = CommunityEventSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = CommunityEvent.objects.all()
        
        # 根据状态筛选
        event_status = self.request.query_params.get('status', None)
        if event_status:
            queryset = queryset.filter(status=event_status)
        
        # 置顶优先，然后按创建时间排序
        queryset = queryset.order_by('-is_pinned', '-created_at')
        
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': '获取社区活动列表成功',
            'events': serializer.data,
            'count': queryset.count()
        })

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'message': '获取社区活动详情成功',
            'event': serializer.data
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': '创建社区活动成功',
                'event': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'message': '创建社区活动失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': '更新社区活动成功',
                'event': serializer.data
            })
        return Response({
            'success': False,
            'message': '更新社区活动失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({
            'success': True,
            'message': '删除社区活动成功'
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """获取进行中的活动"""
        events = CommunityEvent.objects.filter(status='active').order_by('-is_pinned', '-created_at')
        serializer = self.get_serializer(events, many=True)
        return Response({
            'success': True,
            'message': '获取进行中的活动成功',
            'events': serializer.data
        })

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """获取即将开始的活动"""
        events = CommunityEvent.objects.filter(status='upcoming').order_by('-is_pinned', '-created_at')
        serializer = self.get_serializer(events, many=True)
        return Response({
            'success': True,
            'message': '获取即将开始的活动成功',
            'events': serializer.data
        })

    @action(detail=True, methods=['post'])
    def toggle_pin(self, request, pk=None):
        """切换活动的置顶状态"""
        if not request.user.is_staff:
            return Response({
                'success': False,
                'message': '无权操作'
            }, status=status.HTTP_403_FORBIDDEN)
        
        instance = self.get_object()
        instance.is_pinned = not instance.is_pinned
        instance.save()
        
        return Response({
            'success': True,
            'message': f'{"置顶" if instance.is_pinned else "取消置顶"}成功',
            'is_pinned': instance.is_pinned
        })

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """获取推荐活动（置顶或热门）"""
        # 获取置顶活动或参与人数最多的活动
        pinned_events = CommunityEvent.objects.filter(is_pinned=True)
        if pinned_events.exists():
            events = pinned_events
        else:
            events = CommunityEvent.objects.all().order_by('-participant_count')[:5]
        
        serializer = self.get_serializer(events, many=True)
        return Response({
            'success': True,
            'message': '获取推荐活动成功',
            'events': serializer.data
        })
