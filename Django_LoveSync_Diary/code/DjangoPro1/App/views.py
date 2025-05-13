from django.shortcuts import render, HttpResponse, reverse


# 首页
async def user_index(requeust):
    return HttpResponse(requeust, 'index.html')
