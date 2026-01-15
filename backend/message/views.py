from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.db import models
from .models import Message, PrivateChat, MESSAGE_TYPES

@login_required
def message_list(request):
    """消息列表页"""
    # 获取消息类型筛选
    message_type = request.GET.get('type')
    # 获取已读/未读筛选
    is_read = request.GET.get('is_read')
    
    # 构建查询集
    messages_query = Message.objects.filter(
        user=request.user,
        is_deleted=False
    )
    
    # 按类型筛选
    if message_type:
        messages_query = messages_query.filter(type=message_type)
    
    # 按已读状态筛选
    if is_read is not None:
        messages_query = messages_query.filter(is_read=is_read.lower() == 'true')
    
    # 分页处理
    paginator = Paginator(messages_query, 10)  # 每页10条
    page = request.GET.get('page', 1)
    
    try:
        message_list = paginator.page(page)
    except PageNotAnInteger:
        message_list = paginator.page(1)
    except EmptyPage:
        message_list = paginator.page(paginator.num_pages)
    
    context = {
        'message_list': message_list,
        'message_types': MESSAGE_TYPES,
        'current_type': message_type,
        'current_is_read': is_read,
        'unread_count': Message.objects.filter(user=request.user, is_read=False, is_deleted=False).count(),
    }
    
    return render(request, 'message/message_list.html', context)

@login_required
def message_detail(request, message_id):
    """消息详情页"""
    message = get_object_or_404(Message, id=message_id, user=request.user, is_deleted=False)
    
    # 标记为已读
    if not message.is_read:
        message.is_read = True
        message.save()
    
    context = {
        'message': message,
        'unread_count': Message.objects.filter(user=request.user, is_read=False, is_deleted=False).count(),
    }
    
    return render(request, 'message/message_detail.html', context)

@login_required
def update_message_status(request):
    """更新消息状态（标为已读/删除）"""
    if request.method == 'POST':
        message_ids = request.POST.getlist('message_ids[]')
        action = request.POST.get('action')
        
        if not message_ids or not action:
            return JsonResponse({'success': False, 'message': '参数错误'})
        
        messages_query = Message.objects.filter(id__in=message_ids, user=request.user)
        
        try:
            if action == 'read':
                # 标为已读
                messages_query.update(is_read=True)
                messages.success(request, '消息已标为已读')
            elif action == 'delete':
                # 软删除
                messages_query.update(is_deleted=True)
                messages.success(request, '消息已删除')
            else:
                return JsonResponse({'success': False, 'message': '无效操作'})
            
            return JsonResponse({
                'success': True,
                'message': '操作成功',
                'unread_count': Message.objects.filter(user=request.user, is_read=False, is_deleted=False).count()
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '请求方式错误'})

@login_required
def get_unread_count(request):
    """获取未读消息数量"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        unread_count = Message.objects.filter(user=request.user, is_read=False, is_deleted=False).count()
        return JsonResponse({'unread_count': unread_count})
    return JsonResponse({'success': False, 'message': '请求方式错误'})

@login_required
def mark_all_read(request):
    """将所有消息标记为已读"""
    if request.method == 'POST':
        # 将所有未读消息标记为已读
        Message.objects.filter(
            user=request.user,
            is_read=False,
            is_deleted=False
        ).update(is_read=True, is_deleted=False)
        
        messages.success(request, '所有消息已标记为已读')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': '所有消息已标记为已读',
                'unread_count': 0
            })
        
        return redirect('message:list')
    
    return JsonResponse({'success': False, 'message': '请求方式错误'})

@login_required
def private_chat_list(request):
    """私信会话列表"""
    # 获取所有参与的私信会话
    from core.models import User
    
    # 获取当前用户发送和接收的所有私信
    sent_chats = PrivateChat.objects.filter(sender=request.user, message__is_deleted=False)
    received_chats = PrivateChat.objects.filter(recipient=request.user, message__is_deleted=False)
    
    # 获取所有唯一的聊天对象
    chat_partners = set()
    for chat in sent_chats:
        chat_partners.add(chat.recipient)
    for chat in received_chats:
        chat_partners.add(chat.sender)
    
    # 构建会话列表，包含最后一条消息和未读消息数
    conversations = []
    for partner in chat_partners:
        # 获取与该用户的所有私信
        partner_chats = PrivateChat.objects.filter(
            ((models.Q(sender=request.user) & models.Q(recipient=partner)) |
             (models.Q(sender=partner) & models.Q(recipient=request.user))),
            message__is_deleted=False
        ).order_by('-message__create_time')
        
        if partner_chats.exists():
            last_message = partner_chats.first()
            # 计算未读消息数
            unread_count = PrivateChat.objects.filter(
                sender=partner,
                recipient=request.user,
                message__is_read=False,
                message__is_deleted=False
            ).count()
            
            conversations.append({
                'partner': partner,
                'last_message': last_message,
                'unread_count': unread_count,
                'chat_count': partner_chats.count()
            })
    
    # 按最后一条消息时间排序
    conversations.sort(key=lambda x: x['last_message'].message.create_time, reverse=True)
    
    context = {
        'conversations': conversations,
        'unread_count': Message.objects.filter(user=request.user, is_read=False, is_deleted=False).count(),
    }
    
    return render(request, 'message/private_chat_list.html', context)

@login_required
def private_chat_detail(request, user_id):
    """私信对话详情页"""
    from core.models import User
    
    try:
        # 获取聊天对象
        chat_partner = User.objects.get(id=user_id)
        
        # 获取与该用户的所有私信
        chat_messages = PrivateChat.objects.filter(
            ((models.Q(sender=request.user) & models.Q(recipient=chat_partner)) |
             (models.Q(sender=chat_partner) & models.Q(recipient=request.user))),
            message__is_deleted=False
        ).order_by('message__create_time')
        
        # 标记接收的消息为已读
        received_messages = Message.objects.filter(
            user=request.user,
            type='private',
            is_read=False,
            is_deleted=False
        ).filter(private_chat__sender=chat_partner)
        received_messages.update(is_read=True)
        
        context = {
            'chat_partner': chat_partner,
            'chat_messages': chat_messages,
            'unread_count': Message.objects.filter(user=request.user, is_read=False, is_deleted=False).count(),
        }
        
        return render(request, 'message/private_chat_detail.html', context)
        
    except User.DoesNotExist:
        messages.error(request, '用户不存在')
        return redirect('message:private_chat_list')

@login_required
def send_private_message(request):
    """发送私信"""
    if request.method == 'POST':
        # 获取参数
        recipient_id = request.POST.get('recipient_id')
        content = request.POST.get('content').strip()
        reply_to_id = request.POST.get('reply_to_id')
        
        if not recipient_id or not content:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': '收件人和内容不能为空'})
            messages.error(request, '收件人和内容不能为空')
            return redirect('message:list')
        
        try:
            from core.models import User
            recipient = User.objects.get(id=recipient_id)
            
            # 禁止给自己发私信
            if recipient.id == request.user.id:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': '不能给自己发送私信'})
                messages.error(request, '不能给自己发送私信')
                return redirect('message:list')
            
            # 创建消息
            message = Message.objects.create(
                user=recipient,
                type='private',
                content=content
            )
            
            # 创建私信扩展
            private_chat = PrivateChat.objects.create(
                message=message,
                sender=request.user,
                recipient=recipient,
                reply_to_id=reply_to_id if reply_to_id else None
            )
            
            success_message = '私信发送成功'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': success_message,
                    'message_id': message.id,
                    'sender_id': request.user.id,
                    'sender_name': request.user.name,
                    'create_time': message.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'content': content
                })
            
            messages.success(request, success_message)
            return redirect('message:private_chat_detail', user_id=recipient.id)
            
        except User.DoesNotExist:
            error_message = '收件人不存在'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': error_message})
            messages.error(request, error_message)
            return redirect('message:list')
        except Exception as e:
            error_message = f'发送失败：{str(e)}'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': error_message})
            messages.error(request, error_message)
            return redirect('message:list')
    
    # GET请求返回发送私信页面
    recipient_id = request.GET.get('recipient_id')
    recipient = None
    if recipient_id:
        try:
            from core.models import User
            recipient = User.objects.get(id=recipient_id)
        except User.DoesNotExist:
            messages.error(request, '收件人不存在')
            return redirect('message:list')
    
    context = {
        'recipient': recipient,
        'unread_count': Message.objects.filter(user=request.user, is_read=False, is_deleted=False).count(),
    }
    
    return render(request, 'message/send_private_message.html', context)
