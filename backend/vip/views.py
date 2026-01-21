from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from core.models import VIPMember, VIPPrivilege

# 会员中心首页
@login_required
def vip_index(request):
    """会员中心首页"""
    # 确保每个用户都有VIPMember记录
    if not hasattr(request.user, 'vip'):
        VIPMember.objects.create(user=request.user)
    
    context = {
        'user': request.user,
    }
    return render(request, 'vip/vip_index.html', context)

# 会员权益页面
@login_required
def vip_benefits(request):
    """会员权益列表"""
    if not hasattr(request.user, 'vip'):
        VIPMember.objects.create(user=request.user)
    
    # 获取所有VIP特权并按照等级从低到高排序
    privileges = VIPPrivilege.objects.all()
    
    # 定义VIP等级顺序，用于排序
    level_order = {
        'normal': 1,
        'bronze': 2,
        'silver': 3,
        'diamond': 4,
        'king': 5,
        'god': 6
    }
    
    # 按照等级顺序排序
    privileges = sorted(privileges, key=lambda p: level_order.get(p.required_level, 0))
    
    # 获取当前用户的VIP等级
    user_vip_level = request.user.vip.level if hasattr(request.user, 'vip') else 'normal'
    
    # 为每个特权添加是否已解锁的属性
    for privilege in privileges:
        privilege.is_unlocked = level_order[privilege.required_level] <= level_order[user_vip_level]
        # 添加等级颜色信息
        vip_member = VIPMember()
        vip_member.level = privilege.required_level
        privilege.level_color = vip_member.get_level_color()
        privilege.level_text_color = vip_member.get_level_text_color()
    
    # 为每个等级添加颜色信息
    vip_levels_with_colors = []
    for level in VIPMember.VIP_LEVELS:
        vip_member = VIPMember()
        vip_member.level = level[0]
        vip_levels_with_colors.append({
            'value': level[0],
            'display': level[1],
            'color': vip_member.get_level_color(),
            'text_color': vip_member.get_level_text_color()
        })
    
    context = {
        'privileges': privileges,
        'user_vip_level': user_vip_level,
        'level_order': level_order,
        'user': request.user,
        'vip_levels': vip_levels_with_colors,
    }
    return render(request, 'vip/vip_benefits.html', context)

# 充值记录页面
@login_required
def recharge_records(request):
    """充值记录查询"""
    # 获取当前用户的充值记录
    records = request.user.vip_orders.all().order_by('-created_at')
    
    # 分页处理
    paginator = Paginator(records, 10)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'vip/recharge_records.html', context)

# 开通/续费会员页面
@login_required
def create_recharge(request):
    """会员充值/开通"""
    # 确保每个用户都有VIPMember记录
    if not hasattr(request.user, 'vip'):
        VIPMember.objects.create(user=request.user)
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        if not amount:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': '请选择充值金额'})
            messages.error(request, '请选择充值金额')
            return redirect('vip:create_recharge')
        
        amount = int(amount)
        # 根据充值金额计算时长（天）
        duration_map = {
            10: 7,
            50: 30,    
            100: 90,  
            200: 180,  
            500: 365, 
            1000: 730,
        }
        
        if amount not in duration_map:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': '无效的充值金额'})
            messages.error(request, '无效的充值金额')
            return redirect('vip:create_recharge')
        
        duration_days = duration_map[amount]
        
        # 更新会员信息
        vip = request.user.vip
        if vip.is_active and vip.end_date > timezone.now():
            # 如果VIP还在有效期内，从到期时间开始续费
            vip.end_date += timezone.timedelta(days=duration_days)
            vip.renewal_count += 1
        else:
            # 如果VIP已过期或未激活，从现在开始计算
            vip.start_date = timezone.now()
            vip.end_date = timezone.now() + timezone.timedelta(days=duration_days)
            vip.is_active = True
            vip.renewal_count = 1
        
        # 更新累计充值金额
        vip.total_recharge += amount
        vip.save()
        
        # 自动更新VIP等级
        vip.update_vip_level()
        
        # 创建充值订单记录
        from core.models import VIPOrder
        from datetime import datetime
        order_number = f"VIP{datetime.now().strftime('%Y%m%d%H%M%S')}{request.user.id:06d}"
        VIPOrder.objects.create(
            user=request.user,
            amount=amount,
            duration=duration_days,
            status='success',
            paid_at=timezone.now(),
            order_number=order_number
        )
        
        success_message = f'充值成功！您的VIP已开通/续费 {duration_days} 天'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': success_message})
        messages.success(request, success_message)
        return redirect('vip:index')
    
    context = {
        'recharge_options': [
            {'amount': 10, 'duration': '7天', 'description': '普通会员'},
            {'amount': 50, 'duration': '1个月', 'description': '青铜VIP体验'},
            {'amount': 100, 'duration': '3个月', 'description': '白银VIP专享'},
            {'amount': 200, 'duration': '6个月', 'description': '钻石VIP特权'},
            {'amount': 500, 'duration': '12个月', 'description': '国王VIP尊享'},
            {'amount': 1000, 'duration': '24个月', 'description': '神VIP终极特权'},
        ]
    }
    return render(request, 'vip/create_recharge.html', context)
