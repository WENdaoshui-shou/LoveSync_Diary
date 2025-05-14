from django.shortcuts import render, HttpResponse, reverse


# 首页
async def user_index(requeust):
    return HttpResponse(requeust, 'index.html')


# 登录
async def user_login(requset):
    if requset.method == 'GET':
        return HttpResponse(requset, 'login.html')


# 注册
async def user_register(request):
    if request.method == 'GET':
        return HttpResponse(request, 'register.html')
