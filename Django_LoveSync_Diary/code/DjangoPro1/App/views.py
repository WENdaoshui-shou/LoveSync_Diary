from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from App.models import *
from django.contrib import messages
from asgiref.sync import sync_to_async
from django.db import IntegrityError, transaction
from django.shortcuts import render, redirect
import re


# 首页
def user_index(request):
    return render(request, 'index.html')


# 登录
def user_login(request, backend='django.contrib.auth.backends.ModelBackend', remember=True):
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
async def user_register(request):
    if request.method == "GET":
        return render(request, 'register.html')
    elif request.method == "POST":
        phone = request.POST.get('username')
        passwd = request.POST.get('password')
        name = request.POST.get('name')
        email = request.POST.get('email')

        # 检查用户名是否存在
        user_exists = await sync_to_async(User.objects.filter(username=phone).exists)()
        if user_exists:
            return render(request, 'register.html', {'messages': '该用户名已被注册'})

        try:
            # 创建用户
            create_user = sync_to_async(User.objects.create_user)
            user = await create_user(
                username=phone,
                password=passwd,
                name=name,
                email=email,
            )

            # 正确的异步登录处理
            login_user = sync_to_async(login)
            await login_user(request, user)

            return redirect('community')

        except IntegrityError as e:
            if 'unique constraint' in str(e).lower():
                return render(request, 'register.html', {'messages': '手机号被注册'})
            return render(request, 'register.html', {'messages': '注册失败，请重试'})
        except Exception as e:
            # 捕获其他异常
            return render(request, 'register.html', {'messages': '注册过程中发生错误, 请稍后再试'})


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

        return render(request, 'community.html', {
            'user': user_data
        })
    return JsonResponse({'status': 'error', 'message': '仅支持 GET 请求'}, status=405)


# 消息
@login_required
async def message(request):
    return render(request, 'message.html')


# 收藏
@login_required
async def favorites(request):
    return render(request, 'favorites.html')


# 相册
@login_required
async def Photo_album(request):
    return render(request, 'Photo_album.html')


# 动态
@login_required
async def moments(request):
    return render(request, 'moments.html')


# 主页
@login_required
async def Personal_Center(request):
    return render(request, 'Personal_Center.html')


# 设置
@login_required
async def settings(request):
    return render(request, 'settings.html')
