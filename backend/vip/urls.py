from django.urls import path
from . import views

app_name = 'vip'

urlpatterns = [
    # 会员中心首页
    path('', views.vip_index, name='index'),
    
    # 会员权益列表
    path('benefits/', views.vip_benefits, name='benefits'),
    
    # 充值记录查询
    path('recharge-records/', views.recharge_records, name='recharge_records'),
    
    # 开通/续费会员
    path('create-recharge/', views.create_recharge, name='create_recharge'),
]