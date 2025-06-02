import os
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from App.models import *
from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_http_methods, require_POST


# 首页
def user_index(request):
    return render(request, 'index.html')


# 登录
def user_login(request):
    if request.user.is_authenticated:
        return redirect('community')  # 已登录用户直接跳转

    if request.method == 'POST':
        username = request.POST.get('username').strip()
        password = request.POST.get('password').strip()

        # 使用Django内置认证系统验证用户
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # 可选：根据是否勾选“记住我”设置不同有效期
            if request.POST.get('remember-me'):
                # 设置会话有效期为 7 天（单位：秒）
                request.session.set_expiry(7 * 24 * 3600)
            else:
                # 关闭浏览器后会话过期（等价于 SESSION_EXPIRE_AT_BROWSER_CLOSE = True）
                request.session.set_expiry(0)

            # 跳转至目标页面或默认社区页面
            next_url = request.POST.get('next') or request.GET.get('next')
            return redirect(next_url or 'community')
        else:
            messages.error(request, '用户名或密码错误，请重新输入')
            return redirect('login')  # 验证失败返回登录页

        # 处理GET请求，渲染登录页面
    return render(request, 'login.html', {
        'next': request.GET.get('next')
    })


# 退出登录
@login_required
def user_logout(request):
    logout(request)  # 使用Django内置logout函数自动处理会话清除
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

        # 检查用户名是否存在
        user_exists = User.objects.filter(username=phone).exists()
        if user_exists:
            return render(request, 'register.html', {'messages': '该用户名已被注册'})

        try:
            # 创建用户
            create_user = User.objects.create_user
            user = create_user(
                username=phone,
                password=passwd,
                name=name,
                email=email,
            )
            login_user = login
            login_user(request, user)

            return redirect('community')

        except IntegrityError as e:
            if 'unique constraint' in str(e).lower():
                return render(request, 'register.html', {'messages': '手机号被注册'})
            return render(request, 'register.html', {'messages': '注册失败，请重试'})
        except Exception:
            # 捕获其他异常
            return render(request, 'register.html', {'messages': '注册过程中发生错误, 请稍后再试'})


# 社区（需登录，同步视图）
@login_required
def community(request):
    if request.method == 'GET':
        user = request.user

        print(f"用户ID: {user.id}")
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
