from django.db import IntegrityError
from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from asgiref.sync import sync_to_async  # 仅在需要异步时保留
from django.contrib.auth.models import User  # 假设使用默认用户模型，如需自定义请替换
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt


# 首页
def user_index(request):
    return render(request, 'index.html')


# 登录（异步视图）
async def user_login(request):
    # 若用户已登录，直接跳转到 community 页面
    if request.user.is_authenticated:
        return redirect('community')

    if request.method == 'POST':
        # 获取表单数据
        username = request.POST.get('username')  # 对应表单中 input 的 name 属性
        password = request.POST.get('password')

        # 验证用户
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # 验证成功，创建 session 并登录用户
            login(request, user)

            # 设置 session 有效期（可选）
            # request.session.set_expiry(3600)  # 1小时后过期

            # 获取重定向参数（如果有），否则默认跳转到 community
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('community')  # 跳转到 community 页面
        else:
            # 验证失败，返回错误信息
            messages.error(request, '用户名或密码错误')

    # GET 请求或验证失败时，渲染登录页面
    return render(request, 'login.html', {
        'next': request.GET.get('next')  # 传递 next 参数到模板
    })


# 退出登录（同步视图）
@login_required
def user_logout(request):
    logout(request)  # 自动清除 Session
    messages.success(request, '您已成功登出')
    return redirect('login')  # 重定向到登录页面


async def user_register(request):
    if request.method == "GET":
        return render(request, 'register.html')
    elif request.method == "POST":
        uname = request.POST.get('uname')
        passwd = request.POST.get('passwd')

        # 检查用户名是否存在（异步包装）
        user_exists = await sync_to_async(User.objects.filter)(username=uname).exists()
        if user_exists:
            return render(request, 'register.html', {'error': '该用户名已被注册'})

        # 创建用户（异步包装）
        try:
            user = await sync_to_async(User.objects.create_user)(
                username=uname,
                password=passwd,
            )
            return redirect('login')
        except IntegrityError:
            return render(request, 'register.html', {'error': '注册失败，请重试'})


# 社区（需登录，同步视图）
@login_required
def community(request):
    if request.method == 'GET':
        user = request.user
        user_data = {
            'id': user.id,
            'username': user.username,
            # 不返回密码！密码属于敏感信息，禁止暴露
        }
        return JsonResponse({
            'status': 'success',
            'data': user_data,
            'message': '用户信息获取成功'
        })
    return JsonResponse({'status': 'error', 'message': '仅支持 GET 请求'}, status=405)


# 消息
async def message(request):
    return redirect(request, 'message.html')


# 收藏
async def favorites(request):
    return redirect(request, 'favorites.html')


# 相册
async def Photo_album(request):
    return redirect(request, 'Photo_album.html')


# 动态
async def moments(request):
    return redirect(request, 'moments.html')


# 主页
async def Personal_Center(request):
    return redirect(request, 'Personal_Center.html')


# 设置
async def settings(request):
    return redirect(request, 'settings.html')
