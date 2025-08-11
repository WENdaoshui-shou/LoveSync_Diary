import os
from datetime import timedelta, datetime
import pytz
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.urls import reverse
from .models import *
from django.db import IntegrityError
from django.views.decorators.http import require_http_methods, require_POST
import uuid
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden
from django.core.cache import cache
from django.conf import settings
from .utils import generate_verify_code, create_verify_image
import logging
from django.shortcuts import render, get_object_or_404
from .models import CollaborativeDocument
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', )
logger = logging.getLogger(__name__)


# 首页
def user_index(request):
    return render(request, 'index.html')


# 情侣绑定
@login_required
def couple_request(request):
    """处理情侣绑定请求"""
    if request.method == 'POST':
        code = request.POST.get('couple_code')

        try:
            target_profile = Profile.objects.get(couple_code=code)
        except Profile.DoesNotExist:
            messages.error(request, '无效的邀请码')
            return redirect('couple_settings')

        # 不能邀请自己
        if target_profile.user == request.user:
            messages.error(request, '不能邀请自己')
            return redirect('couple_settings')

        try:
            request.user.profile.send_couple_request(target_profile)
            messages.success(request, f'已向 {target_profile.user.username} 发送情侣邀请')
        except ValidationError as e:
            messages.error(request, str(e))

        return redirect('couple_settings')

    return render(request, 'couple/request.html')


@login_required
def couple_accept(request, profile_id):
    """接受情侣请求"""
    target_profile = get_object_or_404(Profile, id=profile_id)

    # 检查是否有待处理的请求
    if request.user.profile.couple_pending != target_profile:
        messages.error(request, '没有待处理的邀请')
        return redirect('couple_settings')

    try:
        request.user.profile.accept_couple_request()
        messages.success(request, f'已与 {target_profile.user.username} 成为情侣')
    except ValidationError as e:
        messages.error(request, str(e))

    return redirect('couple_settings')


@login_required
def couple_reject(request, profile_id):
    """拒绝情侣请求"""
    target_profile = get_object_or_404(Profile, id=profile_id)

    # 检查是否有待处理的请求
    if request.user.profile.couple_pending != target_profile:
        messages.error(request, '没有待处理的邀请')
        return redirect('couple_settings')

    try:
        request.user.profile.reject_couple_request()
        messages.success(request, f'已拒绝 {target_profile.user.username} 的情侣邀请')
    except ValidationError as e:
        messages.error(request, str(e))

    return redirect('couple_settings')


@login_required
def couple_breakup(request):
    """解除情侣关系"""
    if request.method == 'POST':
        try:
            request.user.profile.break_up()
            messages.success(request, '已解除情侣关系')
        except ValidationError as e:
            messages.error(request, str(e))

        return redirect('couple_settings')

    return render(request, 'couple/breakup_confirm.html')


@login_required
def couple(request):
    """情侣设置页面"""
    user = request.user
    profile = user.profile
    context = {
        'user': user,
        'has_couple': user.profile.couple is not None,
        'pending_request': user.profile.couple_pending,
        'received_request': Profile.objects.filter(couple_pending=profile).first() if not profile.couple else None
    }
    return render(request, 'couple.html', context)


# 生成验证码视图
def verify_code(request):
    # 生成随机验证码文本
    code = generate_verify_code()
    # 生成唯一标识（用于Redis存储键）
    code_id = str(uuid.uuid4())
    # 存储验证码到Redis（键：verify_code:{code_id}，值：code）
    cache_key = f"verify_code:{code_id}"
    cache.set(cache_key, code, timeout=settings.VERIFY_CODE_EXPIRE)
    # 生成验证码图片
    image_buffer = create_verify_image(code)
    # 将code_id存入cookie，用于前端提交时关联
    response = HttpResponse(image_buffer, content_type="image/png")
    response.set_cookie("code_id", code_id, max_age=settings.VERIFY_CODE_EXPIRE)
    return response


@csrf_exempt
# 登录
def user_login(request):
    if request.user.is_authenticated:
        return redirect('community')  # 已登录用户直接跳转

    if request.method == 'POST':
        username = request.POST.get('username').strip()
        password = request.POST.get('password').strip()
        user_verify_code = request.POST.get('verify_code', '').upper()  # 获取用户输入的验证码并转为大写
        code_id = request.COOKIES.get('code_id')  # 从cookie获取验证码ID

        # 验证码验证
        if not code_id:
            messages.error(request, '验证码已过期，请刷新重试')
            return render(request, 'login.html')

        cache_key = f"verify_code:{code_id}"
        real_code = cache.get(cache_key)

        if real_code is None:
            messages.error(request, '验证码已过期，请刷新重试')
            return render(request, 'login.html')

        if not user_verify_code:
            messages.error(request, '请填写验证码')
            return render(request, 'login.html')

        if user_verify_code.upper() != real_code.upper():
            messages.error(request, '验证码错误')
            return render(request, 'login.html')

        # 验证码验证通过后删除缓存
        cache.delete(cache_key)

        # 继续原有用户认证逻辑
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if request.POST.get('remember-me'):
                request.session.set_expiry(7 * 24 * 3600)
            else:
                request.session.set_expiry(0)

            next_url = request.POST.get('next') or request.GET.get('next')
            return redirect(next_url or 'community')
        else:
            messages.error(request, '用户名或密码错误，请重新输入')
            return redirect('login')

    return render(request, 'login.html', {
        'next': request.GET.get('next')
    })


# 退出登录
@login_required
def user_logout(request):
    logout(request)
    # 清除会话数据
    request.session.flush()

    # 设置会话立即过期
    request.session.set_expiry(0)

    # 删除客户端 Cookie
    response = redirect('login')
    if 'sessionid' in request.COOKIES:
        response.delete_cookie('sessionid')

    return response


# 注册
def user_register(request):
    if request.method == "GET":
        return render(request, 'register.html')
    elif request.method == "POST":
        name = request.POST.get('name')
        phone = request.POST.get('username')
        passwd = request.POST.get('password')
        email = request.POST.get('email')
        user_verify_code = request.POST.get('verify_code', '').upper()
        code_id = request.COOKIES.get('code_id')

        # 验证码验证
        if not code_id:
            messages.error(request, '验证码已过期，请刷新重试')
            return render(request, 'register.html')

        cache_key = f"verify_code:{code_id}"
        real_code = cache.get(cache_key)

        if real_code is None:
            messages.error(request, '验证码已过期，请刷新重试')
            return render(request, 'register.html')

        if not user_verify_code:
            messages.error(request, '请填写验证码')
            return render(request, 'register.html')

        if user_verify_code.upper() != real_code.upper():
            messages.error(request, '验证码错误')
            return render(request, 'register.html')

        # 验证通过后删除缓存
        cache.delete(cache_key)

        # 检查用户名是否存在
        user_exists = User.objects.filter(username=phone).exists()
        if user_exists:
            messages.error(request, '该手机号已被注册')
            return render(request, 'register.html')

        try:
            user = User.objects.create_user(
                username=phone,
                password=passwd,
                email=email,
            )
            if hasattr(user, 'name'):
                user.name = name
                user.save()

            login(request, user)
            return redirect('community')

        except IntegrityError as e:
            if 'unique constraint' in str(e).lower():
                messages.error(request, '手机号已被注册')
            else:
                messages.error(request, '注册失败，请重试')
            return render(request, 'register.html')
        except Exception as e:
            messages.error(request, '注册过程中发生错误, 请稍后再试')
            return render(request, 'register.html')


# 社区（需登录，同步视图）
@login_required
def community(request):
    if request.method == 'GET':
        user = request.user

        print(f"用户ID: {user.id} ")
        print(f"头像路径: {user.profile.userAvatar}")  # 调试输出

        # 只显示已分享的动态
        moment = Moment.objects.filter(is_shared=True).select_related('user__profile').order_by('-created_at')

        return render(request, 'community.html', {
            'user': request.user,
            'moments': moment,
        })
    return JsonResponse({'status': 'error', 'message': '仅支持 GET 请求'}, status=405)


# 消息
@login_required
def message(request):
    if request.method == 'GET':
        user = request.user

        print(f"用户ID: {user.id}")
        print(f"头像路径: {user.profile.userAvatar}")  # 调试输出

        moment = Moment.objects.filter(user=request.user).select_related('user__profile').all()

        return render(request, 'message.html', {
            'user': request.user,
            'moments': moment,
        })


# 收藏
@login_required
def favorites(request):
    if request.method == 'GET':
        user = request.user

        print(f"用户ID: {user.id}")
        print(f"头像路径: {user.profile.userAvatar}")  # 调试输出

        moment = Moment.objects.filter(user=request.user).select_related('user__profile').all()

        return render(request, 'favorites.html', {
            'user': request.user,
            'moments': moment,
        })


# 相册
@login_required
def photo_album(request):
    if request.method == 'GET':
        user = request.user

        print(f"用户ID: {user.id}")
        print(f"头像路径: {user.profile.userAvatar}")  # 调试输出

        moment = Moment.objects.filter(user=request.user).select_related('user__profile').order_by('-created_at')
        photo = Photo.objects.filter(user=request.user).order_by('-uploaded_at')

        return render(request, 'photo_album.html', {
            'user': request.user,
            'moments': moment,
            'photos': photo,
        })

    if request.method == 'POST':
        # 处理照片上传
        description = request.POST.get('description', '').strip()
        images = request.FILES.getlist('images')  # 获取上传的图片（多张）

        photos = Photo.objects.filter(user=request.user).order_by('-uploaded_at')

        # 验证至少上传了一张图片
        if not images:
            return render(request, 'photo_album.html', {
                'error': '请选择至少一张图片上传',
                'photos': photos
            })

        try:
            # 为每张上传的图片创建Photo对象
            for image in images:
                Photo.objects.create(
                    user=request.user,
                    image=image,
                    description=description,
                )

            return redirect('photo_album')

        except Exception as e:
            return render(request, 'photo_album.html', {
                'error': f'上传失败: {str(e)}',
                'photos': photos
            })


# 删除照片
@login_required
@require_http_methods(['DELETE', 'POST'])
def delete_photo(request, photo_id):
    # 获取当前用户的照片对象，不存在或非所有者则返回404
    photo = get_object_or_404(Photo, id=photo_id, user=request.user)

    try:
        # 删除照片文件
        if photo.image:
            photo.image.delete(save=False)  # 先删除物理文件

        # 删除数据库记录
        photo.delete()

        return JsonResponse({'status': 'success', 'message': '照片删除成功'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# 照片下载
@login_required
def download_photo(request, photo_id):
    """处理照片下载请求"""
    # 获取照片对象
    photo = get_object_or_404(Photo, id=photo_id)

    # 权限检查（确保用户有权限下载）
    # 1. 照片所有者
    # 2. 已共享给伴侣的照片
    if photo.user != request.user and not photo.is_shared_with_partner(request.user):
        raise PermissionDenied("你没有权限下载这张照片")

    # 获取照片文件路径
    file_path = os.path.join(settings.MEDIA_ROOT, str(photo.image))

    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise Http404("照片文件不存在")

    # 读取文件内容
    with open(file_path, 'rb') as f:
        file_content = f.read()

    # 构建响应
    response = HttpResponse(file_content, content_type='image/jpeg')

    # 设置下载文件名（使用原始文件名或自定义）
    original_filename = os.path.basename(photo.image.name)
    response['Content-Disposition'] = f'attachment; filename="{original_filename}"'

    # 设置文件大小
    response['Content-Length'] = os.path.getsize(file_path)

    return response


# 动态
def moments(request):
    if request.method == 'GET':
        user = request.user

        print(f"用户ID: {user.id}")
        print(f"头像路径: {user.profile.userAvatar}")  # 调试输出

        moment = Moment.objects.filter(user=request.user).select_related('user__profile').order_by('-created_at')

        return render(request, 'moments.html', {
            'user': request.user,
            'moments': moment,
        })

    elif request.method == 'POST':
        content = request.POST.get('content', '').strip()
        tags = request.POST.getlist('tags')  # 获取选中的标签
        images = request.FILES.getlist('image')  # 获取多图

        # 验证内容非空
        if not content:
            return render(request, 'moments.html', {
                'moments': Moment.objects.all(),
                'error': '动态内容不能为空'
            })

        try:
            # 创建动态
            moment = Moment.objects.create(
                user=request.user,
                content=content,
                likes=0,
                comments=0
            )

            # 处理标签
            for tag_name in tags:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                moment.tags.add(tag)

            # 处理多图
            for img in images:
                MomentImage.objects.create(moment=moment, image=img)

            return redirect('moments')  # 重定向到动态列表

        except Exception as e:
            return render(request, 'moments.html', {
                'moments': Moment.objects.all(),
                'error': f'发布失败：{str(e)}'
            })


# 分享动态
@login_required
@require_POST
def share_moment(request, moment_id):
    try:
        moment = Moment.objects.get(id=moment_id)

        # 关键校验：防止重复分享
        if moment.is_shared:
            return JsonResponse({'success': False, 'error': '此动态已分享'})

        if moment.user != request.user:
            return JsonResponse({'success': False, 'error': '你无权分享此动态'})

        moment.is_shared = True
        moment.save()

        return JsonResponse({'success': True, 'message': '分享成功'})

    except Moment.DoesNotExist:
        return JsonResponse({'success': False, 'error': '动态不存在'})


# 取消分享动态
@login_required
@require_POST
def unshare_moment(request, moment_id):
    try:
        moment = Moment.objects.get(id=moment_id)

        # 检查用户权限
        if moment.user != request.user:
            return JsonResponse({'success': False, 'error': '无权限'}, status=403)

        # 取消分享
        moment.is_shared = False
        moment.save()

        return JsonResponse({'success': True, 'message': '已取消分享'})

    except Moment.DoesNotExist:
        return JsonResponse({'success': False, 'error': '动态不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# 删除动态
@login_required
@require_http_methods(['DELETE'])
def delete_moment(request, moment_id):
    moment = get_object_or_404(Moment, id=moment_id, user=request.user)
    moment.delete()
    return JsonResponse({'status': 'success'})


# 双人日记
@login_required
def lovesync(request):
    if request.method == "GET":
        user_id = request.user.id
        couple_id = request.user.profile.couple.user_id if request.user.profile.couple else None

        # 构建查询条件：用户自己的所有日记 + 情侣分享的日记
        base_filters = Q(user_id=user_id)  # 自己的所有日记

        # 如果有情侣，添加情侣分享的日记
        if couple_id:
            base_filters |= Q(user_id=couple_id, is_shared=True)

        # 获取前端传递的查询日期参数
        query_date = request.GET.get('query_date')

        # 基础查询集
        all_notes = Note.objects.filter(base_filters).order_by('-created_at')

        # 初始化筛选后的查询集
        filtered_notes = all_notes
        # 存储查询的目标日期（用于无结果时显示）
        target_date = None

        # 如果有查询日期，筛选该日期的日记
        if query_date:
            try:
                # 将字符串转换为日期对象
                target_date = datetime.strptime(query_date, '%Y-%m-%d').date()
                tz = pytz.timezone('Asia/Shanghai')
                # 构造带时区的日期范围
                start_date = tz.localize(datetime.combine(target_date, datetime.min.time()))
                end_date = tz.localize(datetime.combine(target_date, datetime.max.time()))

                # 使用范围查询替代日期查询
                filtered_notes = all_notes.filter(created_at__gte=start_date, created_at__lte=end_date)
            except ValueError:
                # 日期格式错误时显示所有日记并清除查询参数
                filtered_notes = all_notes
                query_date = None  # 清除错误的日期参数
                target_date = None
        else:
            # 没有查询日期时显示所有日记
            filtered_notes = all_notes

        # 按日期分组日记
        grouped_notes = {}
        for note in filtered_notes:
            date_key = note.created_at.date()  # 按年月日分组
            if date_key not in grouped_notes:
                grouped_notes[date_key] = []
            grouped_notes[date_key].append(note)

        # 关键修改：如果有查询日期但没有结果，手动添加该日期到分组中
        if query_date and target_date and target_date not in grouped_notes:
            grouped_notes[target_date] = []

        # 处理日期标题（今天/昨天/具体日期，今年不显示年份）
        formatted_groups = []
        today = timezone.now().date()
        current_year = today.year  # 获取当前年份用于判断

        # 按日期倒序排列
        for date, notes in sorted(grouped_notes.items(), reverse=True):
            date_diff = (today - date).days
            if date_diff == 0:
                date_title = "今天"
            elif date_diff == 1:
                date_title = "昨天"
            else:
                if date.year == current_year:
                    date_title = date.strftime("%m月%d日")
                else:
                    date_title = date.strftime("%Y年%m月%d日")

            formatted_groups.append({
                'date_title': date_title,
                'date': date,
                'notes': notes
            })

        # 心情统计
        mood_counts = {choice[0]: 0 for choice in Note.MOOD_CHOICES}
        for note in filtered_notes:
            mood_counts[note.mood] += 1

        mood_stats = []
        for mood, count in mood_counts.items():
            temp_note = Note(mood=mood)
            mood_stats.append({
                'mood': mood,
                'count': count,
                'color': temp_note.get_mood_color(),
                'icon': temp_note.get_mood_icon(),
                'display': temp_note.get_mood_display_text(),
                'css_class': mood,
            })
        mood_stats.sort(key=lambda x: x['count'], reverse=True)

        # 日记数量统计
        user_notes_count = filtered_notes.filter(user_id=user_id).count()
        partner_notes_count = filtered_notes.filter(user_id=couple_id).count() if couple_id else 0

        # 月度统计
        monthly_stats = {}
        for note in all_notes:  # 月度统计基于所有日记，不受日期查询影响
            month_key = note.created_at.strftime("%Y-%m")
            if month_key not in monthly_stats:
                monthly_stats[month_key] = {
                    'year': note.created_at.year,
                    'month': note.created_at.month,
                    'count': 0
                }
            monthly_stats[month_key]['count'] += 1
        monthly_list = sorted(monthly_stats.values(), key=lambda x: (x['year'], x['month']), reverse=True)

        return render(request, 'lovesync.html', {
            'grouped_notes': formatted_groups,
            'mood_stats': mood_stats,
            'monthly_stats': monthly_list,
            'total_notes': filtered_notes.count(),
            'user_notes_count': user_notes_count,
            'partner_notes_count': partner_notes_count,
            'query_date': query_date,  # 将查询日期回传给模板
            'target_date': target_date,  # 传递目标日期对象给模板
        })

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

            return JsonResponse({
                'success': True,
                'message': '日记保存成功',
                'id': note.id
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)

    return JsonResponse({
        'success': False,
        'message': '方法不允许'
    }, status=405)


# 主页
@login_required
def personal_center(request):
    if request.method == 'GET':
        user = request.user

        print(f"用户ID: {user.id}")
        print(f"头像路径: {user.profile.userAvatar}")  # 调试输出
        print(f"情侣ID: {user.profile.couple.user.id}")  # 调试输出

        moment = Moment.objects.filter(user=request.user).select_related('user__profile').all()

        return render(request, 'personal_center.html', {
            'user': request.user,
            'moments': moment,
        })


# 设置
def settings_view(request, tab='profile'):
    if request.method == 'GET':
        user = request.user
        print(f"用户ID: {user.id}")
        print(f"头像路径: {user.profile.userAvatar}")  # 调试输出
        print(f": {user.profile.couple_joined_at}")  # 调试输出

        moment = Moment.objects.filter(user=request.user).select_related('user__profile').all()

        return render(request, 'settings.html', {
            'user': request.user,
            'moments': moment,
        })

    if request.method == 'POST':
        profile = request.user.profile

        if tab == 'profile':
            # 处理个人信息表单
            # 更新 User 模型的昵称
            request.user.name = request.POST.get('name', request.user.name)
            request.user.save()

            # 更新 Profile 模型的其他信息
            profile.gender = request.POST.get('gender', profile.gender)
            birth_date = request.POST.get('birth_date')
            profile.birth_date = birth_date if birth_date else None
            profile.location = request.POST.get('location', profile.location)
            profile.bio = request.POST.get('bio', profile.bio)

            # 处理头像上传
            if 'userAvatar' in request.FILES:
                # # 删除旧头像
                if profile.userAvatar:
                    old_avatar_path = profile.userAvatar.path
                    if os.path.exists(old_avatar_path):
                        os.remove(old_avatar_path)
                profile.userAvatar = request.FILES['userAvatar']

            profile.save()
            messages.success(request, '个人信息已成功更新！')
            return redirect('settings', tab='profile')

        # 处理 GET 请求时渲染模板
        return render(request, 'settings.html')


# 评论
@login_required
def add_comment(request, moment_id, parent_id=None):
    try:
        moment = get_object_or_404(Moment, id=moment_id)
        parent_comment = None

        # 验证父评论（如果有）
        if parent_id:
            parent_comment = get_object_or_404(Comment, id=parent_id, moment=moment)

        content = request.POST.get('content', '').strip()
        if not content:
            return JsonResponse({'status': 'error', 'message': '评论内容不能为空'}, status=400)

        # 创建评论
        comment = Comment.objects.create(
            moment=moment,
            user=request.user,
            parent=parent_comment,
            content=content
        )

        # 序列化评论数据
        def serialize_comment(comment):
            return {
                'id': comment.id,
                'user': {
                    'username': comment.user.username,
                    'avatar': comment.user.profile.userAvatar.url if hasattr(comment.user, 'profile') else None
                },
                'content': comment.content,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
                'is_parent': comment.parent_id is None,
                'replies_count': comment.replies.count()
            }

        return JsonResponse({
            'status': 'success',
            'comment': serialize_comment(comment),
            'total_comments': moment.comment_set.count()
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# 删除评论
def delete_comment(request, comment_id):
    try:
        comment = get_object_or_404(Comment, id=comment_id, user=request.user)
        moment_id = comment.moment.id

        # 删除前获取评论总数（用于前端更新）
        total_comments = comment.moment.comment_set.count()

        # 执行删除（级联删除所有子评论）
        comment.delete()

        return JsonResponse({
            'status': 'success',
            'moment_id': moment_id,
            'total_comments': total_comments - 1
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# 推荐商品
def recommend_view(func):
    def _wrapper(request, *args, **kwargs):
        # 从cookie中获取用户访问的所有商品id
        c_id = request.COOKIES.get('rem', '')

        # 存放用户访问商品的id列表，使用逗号分隔
        visited_ids = [gid for gid in c_id.split(',') if gid.strip()]

        # 构建推荐商品列表（这里使用简单逻辑，实际项目中可根据需求优化）
        recommended_products = []
        if visited_ids:
            # 从用户访问过的商品中推荐前3个（如果有）
            recommended_products = Product.objects.filter(id__in=visited_ids[:5])

        # 将推荐商品添加到请求对象中
        request.recommended_products = recommended_products

        # 调用原视图函数
        response = func(request, *args, **kwargs)

        # 获取当前查看的商品ID（如果有）
        current_product_id = request.GET.get('product_id')
        if current_product_id and current_product_id not in visited_ids:
            # 将当前商品ID添加到访问历史的最前面
            visited_ids.insert(0, current_product_id)
            # 限制历史记录长度为10个商品
            if len(visited_ids) > 10:
                visited_ids = visited_ids[:10]
            # 更新cookie
            response.set_cookie('rem', ','.join(visited_ids), max_age=24 * 60 * 60)

        return response

    return _wrapper


# 购物商城
@login_required
@recommend_view
def mall(request, recommended_products=None):
    products = Product.objects.all()

    # 如果装饰器提供了推荐商品，则使用它们
    if recommended_products is None:
        # 否则使用默认的随机推荐
        recommended_products = Product.objects.order_by('?')[:5]

    hot_products = Product.objects.order_by('-monthly_sales')[:3]

    return render(request, 'mall.html', {
        'products': products,
        'recommended_products': recommended_products,
        'hot_products': hot_products
    })


# 商品详情
@recommend_view
def product_detail(request, product_id):
    """商品详情视图"""
    product = get_object_or_404(Product, id=product_id)

    # 从请求对象中获取推荐商品
    recommended_products = getattr(request, 'recommended_products', [])
    if not recommended_products:
        recommended_products = Product.objects.order_by('-rating')[:5]

    hot_products = Product.objects.order_by('-monthly_sales')[:3]

    return render(request, 'product_detail.html', {
        'product': product,
        'recommended_products': recommended_products,
        'hot_products': hot_products
    })


# 添加商品到购物车
@login_required
@require_POST
def add_to_cart(request):
    try:
        # 1. 获取请求参数
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))

        # 2. 验证参数有效性
        if not product_id or quantity <= 0:
            return JsonResponse({
                'status': 'error',
                'message': '无效的商品ID或数量'
            }, status=400)

        # 3. 获取商品并验证库存
        product = get_object_or_404(Product, id=product_id)
        if product.product_stock < quantity:
            return JsonResponse({
                'status': 'error',
                'message': f'库存不足，当前仅剩余{product.product_stock}件'
            }, status=400)

        # 4. 同步数据库：创建或更新购物车记录
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            # 已存在则累加数量
            cart_item.quantity += quantity
            cart_item.save()

        # 5. 同步缓存：更新Redis缓存（提升读取速度）
        user_id = request.user.id
        cart_key = f'user_cart:{user_id}'  # 缓存键格式：user_cart:用户ID
        cart = cache.get(cart_key, {})  # 从缓存获取当前购物车

        # 更新缓存中的商品信息
        cart[str(product_id)] = {
            'id': product_id,
            'name': product.name,
            'price': str(product.price),
            'quantity': cart_item.quantity,
        }
        cache.set(cart_key, cart, timeout=86400)  # 缓存1天

        # 6. 扣减商品库存
        product.product_stock -= quantity
        product.save()

        return JsonResponse({
            'status': 'success',
            'message': f'已将{product.name}加入购物车',
            'cart_count': sum(item['quantity'] for item in cart.values())  # 购物车总数量
        })

    except ValueError:
        return JsonResponse({
            'status': 'error',
            'message': '数量必须是有效数字'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'操作失败：{str(e)}'
        }, status=500)


# 获取购物车商品总数
@login_required
def cart_count(request):
    user_id = request.user.id
    cart_key = f'user_cart:{user_id}'
    cart = cache.get(cart_key, {})
    count = sum(item['quantity'] for item in cart.values())
    return JsonResponse({'count': count})


# 购物车
@login_required
def mallcart(request):
    user_id = request.user.id
    cart_key = f'user_cart:{user_id}'
    cart = cache.get(cart_key)
    # 缓存失效时从数据库加载并更新缓存
    if cart:
        cart_items = CartItem.objects.filter(user=request.user).select_related('product')
        cart = {
            str(item.product.id): {
                'name': item.product.name,
                'price': str(item.product.price),
                'quantity': item.quantity,
                'image': item.product.image.url
            } for item in cart_items
        }
        print(cart)
        cache.set(cart_key, cart, timeout=86400)

    return render(request, 'mallcart.html', {'cart_items': cart})


# 更新购物车
@login_required
def update_cart(request):
    if request.method == 'POST':
        try:
            # 解析前端发送的JSON数据
            cart_data = json.loads(request.body)
            user = request.user
            cart_key = f'user_cart:{user.id}'

            # 获取用户当前所有购物车项
            existing_items = {
                item.product.id: item
                for item in CartItem.objects.filter(user=user)
            }

            # 处理前端发送的每个商品
            for product_id, item_data in cart_data.items():
                try:
                    product_id_int = int(product_id)
                    product = Product.objects.get(id=product_id_int)

                    # 检查商品是否已在购物车中
                    if product_id_int in existing_items:
                        # 更新现有商品数量
                        cart_item = existing_items[product_id_int]
                        cart_item.quantity = item_data['quantity']
                        cart_item.save()
                        del existing_items[product_id_int]
                    else:
                        # 添加新商品到购物车
                        CartItem.objects.create(
                            user=user,
                            product=product,
                            quantity=item_data['quantity']
                        )
                except (ValueError, Product.DoesNotExist):
                    # 忽略无效的商品ID
                    continue

            # 删除前端购物车中已不存在的商品
            for remaining_item in existing_items.values():
                remaining_item.delete()

            # 更新缓存
            updated_items = CartItem.objects.filter(user=user).select_related('product')
            updated_cart = {
                str(item.product.id): {
                    'name': item.product.name,
                    'price': str(item.product.price),
                    'quantity': item.quantity,
                    'image': item.product.image.url
                } for item in updated_items
            }
            cache.set(cart_key, updated_cart, timeout=86400)

            return JsonResponse({
                'success': True,
                'message': '购物车已更新',
                'item_count': updated_items.count()
            })

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': '无效的JSON数据'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    # 处理非POST请求
    return JsonResponse({'success': False, 'message': '仅支持POST请求'}, status=405)


# 收藏
@login_required
def mallmark(request):
    return render(request, 'mallmark.html')


# 结算视图
@login_required
def checkout(request, product_id=None):
    user_id = request.user.id
    cart_key = f'user_cart:{user_id}'
    cart = cache.get(cart_key, {})
    return render(request, 'checkout.html', {'cart_items': cart, 'product_id': product_id})


@login_required
def collaborative_editor(request, document_id):
    document = get_object_or_404(CollaborativeDocument, id=document_id)

    # 检查权限：只有文档所有者或其情侣可以访问
    if request.user != document.owner and (document.couple is None or request.user != document.couple.user):
        return HttpResponseForbidden("你无权访问此文档")

    return render(request, 'collaborative_editor.html', {
        'document': document
    })


@csrf_exempt
@login_required
def create_document(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        document = CollaborativeDocument.objects.create(
            title=data.get('title', '新文档'),
            owner=request.user,
            content=data.get('content', '')
        )
        # 关联情侣（如果存在）
        try:
            profile = request.user.profile
            if profile.couple:
                document.couple = profile
                document.save()
        except:
            pass

        return JsonResponse({
            'id': document.id,
            'title': document.title,
            'content': document.content,
            'url': reverse('collaborative_editor', args=[document.id])
        }, status=201)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def couple_recommendation(request):
    if request.method == 'GET':
        return render(request, 'couple_recommendation.html')


def couple_places(request):
    if request.method == 'GET':
        return render(request, 'couple_places.html')


def couple_test(request):
    if request.method == 'GET':
        return render(request, 'couple_test.html')
