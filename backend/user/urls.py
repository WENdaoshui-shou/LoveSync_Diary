from django.urls import path
from . import views

app_name = 'user'  # URL命名空间

urlpatterns = [
    path('profile/<int:user_id>/', views.profile, name='profile'),  # 用户主页
    path('follow/', views.follow, name='follow'),  # 关注用户
    path('unfollow/', views.unfollow, name='unfollow'),  # 取消关注
    path('get-followers/<int:user_id>/', views.get_followers, name='get_followers'),  # 获取粉丝列表
    path('get-following/<int:user_id>/', views.get_following, name='get_following'),  # 获取关注列表
    path('load-more-moments/<int:user_id>/', views.load_more_moments, name='load_more_moments'),  # 加载更多动态
]