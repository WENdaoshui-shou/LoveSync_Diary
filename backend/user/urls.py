from django.urls import path
from user import views

app_name = 'user'  # URL命名空间

urlpatterns = [
    path('profile/<int:user_id>/', views.profile, name='profile'),  # 用户主页
    path('follow/', views.follow, name='follow'),  # 关注用户
    path('unfollow/', views.unfollow, name='unfollow'),  # 取消关注
    path('get-followers/<int:user_id>/', views.get_followers, name='get_followers'),  # 获取粉丝列表
    path('get-following/<int:user_id>/', views.get_following, name='get_following'),  # 获取关注列表
    path('load-more-moments/<int:user_id>/', views.load_more_moments, name='load_more_moments'),  # 加载更多动态
    
    # 收藏相关API路由
    path('api/collection/add/', views.add_collection, name='add_collection'),  # 添加收藏
    path('api/collection/remove/', views.remove_collection, name='remove_collection'),  # 取消收藏
    path('api/collection/list/', views.get_collections, name='get_collections'),  # 获取收藏列表
    
    # 收藏页面路由
    path('collections/', views.collections, name='collections'),  # 收藏页面
    
    # 从core应用移动过来的路由
    path('achievements/', views.achievements_view, name='achievements'),  # 成就页面
    path('achievements/data/', views.get_achievements_data, name='get_achievements_data'),  # 成就数据API
    path('follow/toggle/', views.follow_toggle, name='follow_toggle'),  # 关注/取消关注接口
    path('following/', views.following_list, name='following_list'),  # 关注列表页面
    path('followers/', views.follower_list, name='follower_list'),  # 粉丝列表页面
    path('user/<str:username>/', views.user_profile, name='user_profile'),  # 用户主页
]