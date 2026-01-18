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
    # 构建查询集 - 只获取未删除的消息
    all_messages = Message.objects.filter(
        user=request.user,
        is_deleted=False
    ).order_by('-create_time')
    
    # 按用户分组，每个用户只显示一条最新消息
    # 对于私信，按sender分组；对于其他消息，按类型分组
    grouped_messages = {}
    for message in all_messages:
        if message.type == 'private' and message.private_chat and message.private_chat.sender:
            # 私信按发送者ID分组，确保只保留最新的一条
            key = f'private_{message.private_chat.sender.id}'
        else:
            # 其他消息类型，每个消息独立显示
            key = f'{message.type}_{message.id}'
        
        # 只保留最新的消息（因为all_messages已经按时间倒序排序）
        if key not in grouped_messages:
            grouped_messages[key] = message
    
    # 转换为列表并按时间倒序排序（确保最新消息在最前）
    sorted_messages = sorted(grouped_messages.values(), key=lambda x: x.create_time, reverse=True)
    
    # 计算未读消息数
    unread_count = Message.objects.filter(user=request.user, is_read=False, is_deleted=False).count()
    
    # 计算总消息数（分组后的数量）
    total_message_count = len(grouped_messages)
    
    # 获取未读消息列表（用于未读消息标签页）
    unread_messages_query = Message.objects.filter(
        user=request.user,
        is_read=False,
        is_deleted=False
    ).order_by('-create_time')
    
    # 按用户分组未读消息
    unread_messages_grouped = {}
    for message in unread_messages_query:
        if message.type == 'private' and message.private_chat and message.private_chat.sender:
            # 私信按发送者ID分组
            key = f'private_{message.private_chat.sender.id}'
        else:
            # 其他消息按类型分组
            key = f'{message.type}_{message.id}'
        
        if key not in unread_messages_grouped:
            unread_messages_grouped[key] = message
    
    # 转换为列表并按时间倒序排序
    unread_messages = sorted(unread_messages_grouped.values(), key=lambda x: x.create_time, reverse=True)
    
    # 获取系统通知列表（用于系统通知标签页）
    system_messages_query = Message.objects.filter(
        user=request.user,
        type='system',
        is_deleted=False
    ).order_by('-create_time')
    
    # 转换为列表
    system_messages = list(system_messages_query)
    
    # 计算系统通知数量
    system_count = len(system_messages)
    
    # 获取私信会话列表数据
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
    if conversations:
        conversations.sort(key=lambda x: x['last_message'].message.create_time, reverse=True)
    
    context = {
        'grouped_messages': grouped_messages,
        'unread_count': unread_count,
        'unread_messages': unread_messages,
        'system_messages': system_messages,
        'system_count': system_count,
        'total_message_count': total_message_count,
        'conversations': conversations,
    }
    
    return render(request, 'message/message_list.html', context)



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
        Message.objects.filter(
            user=request.user,
            is_read=False,
            is_deleted=False
        ).update(is_read=True)
        
        unread_count = Message.objects.filter(
            user=request.user,
            is_read=False,
            is_deleted=False
        ).count()
        
        return JsonResponse({
            'success': True,
            'message': '所有消息已标记为已读',
            'unread_count': unread_count
        })
    
    return JsonResponse({'success': False, 'message': '仅支持POST请求'}, status=405)

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
        return redirect('message:list')

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
