import os
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from App.models import *
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_http_methods, require_POST
import uuid
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponse
from django.core.cache import cache
from django.conf import settings
from .utils import generate_verify_code, create_verify_image


# 首页
def user_index(request):
    return render(request, 'index.html')


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
            logger.error(f"注册异常: {str(e)}")
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
    if request.method == 'GET':
        user = request.user

        print(f"用户ID: {user.id}")
        print(f"头像路径: {user.profile.userAvatar}")  # 调试输出

        moment = Moment.objects.filter(user=request.user).select_related('user__profile').all()

        return render(request, 'lovesync.html', {
            'user': request.user,
            'moments': moment,
        })


# 主页
@login_required
def personal_center(request):
    if request.method == 'GET':
        user = request.user

        print(f"用户ID: {user.id}")
        print(f"头像路径: {user.profile.userAvatar}")  # 调试输出

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


# 购物商城
def mall(request):
    return render(request, 'mall.html')


# 购物车
def mallcart(request):
    return render(request, 'mallcart.html')


# 收藏
def mallmark(request):
    return render(request, 'mallmark.html')
