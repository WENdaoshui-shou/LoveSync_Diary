from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'vip'

# API路由
api_router = DefaultRouter()
api_router.register(r'vip', views.VIPMemberViewSet, basename='vip')
api_router.register(r'privileges', views.VIPPrivilegeViewSet, basename='vip_privilege')
api_router.register(r'orders', views.VIPOrderViewSet, basename='vip_order')

urlpatterns = [
    # 会员中心首页
    path('', views.vip_index, name='index'),
    
    # 会员权益列表
    path('benefits/', views.vip_benefits, name='benefits'),
    
    # 充值记录查询
    path('recharge-records/', views.recharge_records, name='recharge_records'),
    
    # 开通/续费会员
    path('create-recharge/', views.create_recharge, name='create_recharge'),
    
    # API路由
    path('api/', include(api_router.urls)),
]