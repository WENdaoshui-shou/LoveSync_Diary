from django.shortcuts import render, HttpResponse, reverse, redirect
from App.models import *


# 首页
async def user_index(request):
    return render(request, 'index.html')


# 登录
async def user_login(request):
    if request.method == "GET":
        # 如果是 GET 请求，返回登录页面
        return render(request, 'login.html')

    elif request.method == "POST":
        # 登录功能
        # 1. 接收前端传来的数据
        uname = request.POST.get('uname')
        passwd = request.POST.get('passwd')

        # 2. 登录验证
        users = User.objects.filter(username=uname, password=passwd).first()
        if users:
            #     # 3. 设置 Cookie
            #     response = redirect(reverse('index'))
            #     response.set_cookie('userid', user.id, max_age=3600)  # 设置 Cookie，有效期为 1 小时
            #     return response
            # else:
            #     # 如果验证失败，返回错误信息
            #     return render(request, 'login.html', {'error': '用户名或密码错误'})
            user = users.first()
            response = redirect(reverse('index'))

            # 3. 设置session
            request.session['userid'] = user.id
            request.session.set_expiry(7 * 24 * 3600)

            # 4.跳转到登录页面
            return response


# 注册
async def user_register(request):
    if request.method == 'GET':
        return render(request, 'register.html')

    elif request.method == 'POST':
        # 接收前端提交过来的数据
        uname = request.POST.get('uname')
        passwd = request.POST.get('passwd')
        print(uname, passwd, sep=' ---- ')

        # 先判断用户是否已经被注册过
        users = User.objects.filter(username=uname)
        if users.exists():
            return HttpResponse('用户名已经存在')

        # 实现注册功能
        try:
            user = User()
            user.username = uname
            user.password = passwd
            user.save()
        except:
            return HttpResponse('注册失败!')

        # 注册成功后跳转到登录页面
        return redirect(reverse('login'))
