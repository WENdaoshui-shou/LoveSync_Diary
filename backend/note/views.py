from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, date, timedelta
import pytz
from .models import Note, NoteImage, Like, Comment
from .serializers import NoteSerializer


SHANGHAI_TZ = pytz.timezone('Asia/Shanghai')

class NoteViewSet(viewsets.ModelViewSet):
    """日记视图集"""
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取日记列表，支持按用户筛选"""
        queryset = self.queryset.order_by('-created_at')
        user_id = self.request.query_params.get('user_id')
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        else:
            # 默认只显示当前用户的日记
            queryset = queryset.filter(user=self.request.user)
        
        return queryset
    
    def perform_create(self, serializer):
        """创建日记"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """分享日记"""
        note = self.get_object()
        note.is_shared = True
        note.save()
        return Response({'is_shared': note.is_shared})
    
    @action(detail=True, methods=['post'])
    def unshare(self, request, pk=None):
        """取消分享日记"""
        note = self.get_object()
        note.is_shared = False
        note.save()
        return Response({'is_shared': note.is_shared})
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """点赞/取消点赞日记"""
        note = self.get_object()
        
        # 检查是否已经点赞
        like, created = Like.objects.get_or_create(user=request.user, note=note)
        
        if created:
            # 增加点赞数
            note.likes = note.likes + 1
            note.save()
            
            return Response({
                'message': '点赞成功',
                'likes': note.likes,
                'is_liked': True
            }, status=200)
        else:
            # 已点赞，取消点赞
            like.delete()
            # 减少点赞数
            note.likes = note.likes - 1 if note.likes > 0 else 0
            note.save()
            
            return Response({
                'message': '取消点赞成功',
                'likes': note.likes,
                'is_liked': False
            }, status=200)
    
    @action(detail=True, methods=['get'])
    def is_liked(self, request, pk=None):
        """检查当前用户是否已点赞该日记"""
        note = self.get_object()
        is_liked = Like.objects.filter(user=request.user, note=note).exists()
        return Response({'is_liked': is_liked}, status=200)
    
    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        """添加评论"""
        note = self.get_object()
        content = request.data.get('content')
        parent_id = request.data.get('parent_id')
        
        if not content:
            return Response({'message': '评论内容不能为空'}, status=400)
        
        comment = Comment.objects.create(
            note=note,
            user=request.user,
            content=content,
            parent_id=parent_id
        )
        
        # 重新统计该日记的所有评论数（含一级+二级）
        total_comments = Comment.objects.filter(note=note).count()
        
        # 更新日记的评论数
        note.comments = total_comments
        note.save()
        
        return Response({
                'message': '评论成功',
                'comments': note.comments,
                'comment': {
                    'id': comment.id,
                    'user': comment.user.name,
                    'avatar': comment.user.profile.userAvatar.url,
                    'content': comment.content,
                    'created_at': comment.created_at,
                    'parent_id': comment.parent_id
                }
            }, status=201)
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """获取日记的评论列表（仅返回一级评论，二级评论包含在replies字段中）"""
        note = self.get_object()
        # 只获取一级评论（parent_id为None）
        main_comments = note.comment_set.filter(parent_id=None)
        
        comments_list = []
        for comment in main_comments:
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
        }, status=200)
    
    @action(detail=True, methods=['delete'], url_path='delete_comment/(?P<comment_id>\d+)')
    def delete_comment(self, request, pk=None, comment_id=None):
        """删除评论/回复（级联删除二级回复）"""
        note = self.get_object()
        
        try:
            # 1. 查询要删除的主评论/回复
            target_comment = Comment.objects.get(id=comment_id, note=note)
            
            # 2. 权限校验：只能删除自己的评论
            if target_comment.user != request.user:
                return Response({
                    'message': '无权限删除该评论'
                }, status=403)
            
            # 3. 关键：如果是主评论（无parent_id），先删除其所有二级回复
            if target_comment.parent_id is None:  # 判定为主评论
                # 删除该主评论下的所有二级回复
                Comment.objects.filter(parent_id=target_comment.id, note=note).delete()
            
            # 4. 删除目标评论（主评论/二级回复）
            target_comment.delete()
            
            # 5. 重新统计该日记的所有评论数（含一级+二级）
            total_comments = Comment.objects.filter(note=note).count()
            
            # 更新日记的评论数
            note.comments = total_comments
            note.save()
            
            return Response({
                'message': '评论删除成功',
                'comments': total_comments  # 返回所有评论数（含一级+二级）
            }, status=200)
        except Comment.DoesNotExist:
            return Response({
                'message': '评论不存在'
            }, status=404)
        except Exception as e:
            return Response({
                'message': f'删除评论失败: {str(e)}'
            }, status=500)


# 双人日记视图
@login_required
def lovesync(request):
    if request.method == "GET":
        if not request.user.is_authenticated:
            return redirect('login')

        user_id = request.user.id
        couple_id = None
        try:
            couple_user = request.user.profile.couple
            if couple_user and hasattr(couple_user, 'user') and couple_user.user:
                couple_id = couple_user.user.id
        except (AttributeError, Exception):
            couple_user = None
            couple_id = None
        
        # 检查用户是否绑定情侣，未绑定则重定向到情侣设置页面
        if not couple_id:
            from django.contrib import messages
            messages.error(request, '请先绑定情侣关系，才能使用双人日记功能')
            return redirect('couple_web:couple')

        base_filters = Q(user_id=user_id)
        if couple_id:
            base_filters |= Q(user_id=couple_id, is_shared=True)
        
        all_notes = Note.objects.filter(base_filters).order_by('-created_at').select_related('user')
        query_date = request.GET.get('query_date')
        filtered_notes = all_notes
        target_date = None

        if query_date:
            try:
                target_date = datetime.strptime(query_date, '%Y-%m-%d').date()
                start_datetime = SHANGHAI_TZ.localize(datetime.combine(target_date, datetime.min.time()))
                end_datetime = SHANGHAI_TZ.localize(datetime.combine(target_date, datetime.max.time()))
                
                filtered_notes = all_notes.filter(created_at__range=(start_datetime, end_datetime))
            except ValueError:
                filtered_notes = all_notes
                query_date = None
                target_date = None

        grouped_notes = {}
        for note in filtered_notes:
            date_key = note.created_at.astimezone(SHANGHAI_TZ).date()
            if date_key not in grouped_notes:
                grouped_notes[date_key] = []
            grouped_notes[date_key].append(note)
        
        if query_date and target_date and target_date not in grouped_notes:
            grouped_notes[target_date] = []

        formatted_groups = []
        today = timezone.now().astimezone(SHANGHAI_TZ).date()
        current_year = today.year

        # 按日期倒序排列
        for date_key, notes in sorted(grouped_notes.items(), key=lambda x: x[0], reverse=True):
            if query_date and date_key == target_date:
                date_title = date_key.strftime("%Y-%m-%d")
            else:
                if date_key.year == current_year:
                    date_title = date_key.strftime("%m月%d日")
                else:
                    date_title = date_key.strftime("%Y年%m月%d日")
            
            formatted_groups.append({
                'date_title': date_title,
                'date': date_key,
                'notes': notes
            })

        mood_counts = Note.objects.filter(base_filters).values('mood').annotate(count=Count('mood')).order_by('-count')
        mood_count_dict = {mood[0]: 0 for mood in Note.MOOD_CHOICES}
        for item in mood_counts:
            mood_count_dict[item['mood']] = item['count']
        
        today_sh = timezone.now().astimezone(SHANGHAI_TZ).date()
        week_start_sh = today_sh - timedelta(days=today_sh.weekday())
        week_start_datetime = SHANGHAI_TZ.localize(datetime.combine(week_start_sh, datetime.min.time()))
        
        weekly_mood_counts = Note.objects.filter(base_filters, created_at__gte=week_start_datetime).values('mood').annotate(count=Count('mood'))
        weekly_mood_dict = {mood[0]: 0 for mood in Note.MOOD_CHOICES}
        for item in weekly_mood_counts:
            weekly_mood_dict[item['mood']] = item['count']

        mood_stats = []
        for mood, count in mood_count_dict.items():
            temp_note = Note(mood=mood)
            mood_stats.append({
                'mood': mood,
                'count': count,
                'weekly_count': weekly_mood_dict[mood],
                'color': temp_note.get_mood_color(),
                'icon': temp_note.get_mood_icon(),
                'display': temp_note.get_mood_display_text(),
                'css_class': mood,
            })
        mood_stats.sort(key=lambda x: x['count'], reverse=True)

        user_notes_count = filtered_notes.filter(user_id=user_id).count()
        partner_notes_count = filtered_notes.filter(user_id=couple_id).count() if couple_id else 0

        monthly_stats = {}
        for note in all_notes:
            note_sh = note.created_at.astimezone(SHANGHAI_TZ)
            month_key = note_sh.strftime("%Y-%m")
            if month_key not in monthly_stats:
                monthly_stats[month_key] = {
                    'year': note_sh.year,
                    'month': note_sh.month,
                    'count': 0
                }
            monthly_stats[month_key]['count'] += 1
        monthly_list = sorted(monthly_stats.values(), key=lambda x: (x['year'], x['month']), reverse=True)

        context = {
            'grouped_notes': formatted_groups,
            'mood_stats': mood_stats,
            'monthly_stats': monthly_list,
            'total_notes': filtered_notes.count(),
            'user_notes_count': user_notes_count,
            'partner_notes_count': partner_notes_count,
            'query_date': query_date,
            'target_date': target_date,
            'couple_id': couple_id,
        }

        return render(request, 'lovesync.html', context)

    if request.method == 'POST':
        try:
            # 处理表单数据
            context = request.POST.get('context')
            mood = request.POST.get('mood')
            is_shared = request.POST.get('share_with_partner', '0') == '1'
            images = request.FILES.getlist('photos')

            # 创建日记实例
            note = Note.objects.create(
                user=request.user,
                context=context,
                mood=mood,
                is_shared=is_shared,
            )

            # 处理上传的图片
            if images:
                for photo in images:
                    NoteImage.objects.create(notemoment=note, noteimage=photo)

            # 重定向到lovesync页面，而不是返回JSON响应
            return redirect('lovesync')
        except Exception as e:
            # 如果出现错误，也重定向到lovesync页面
            return redirect('lovesync')

    from django.http import HttpResponseNotAllowed
    return HttpResponseNotAllowed(['GET', 'POST'])