from django.urls import path
from . import views

app_name = 'history'

urlpatterns = [
    path('index/', views.history_index, name='index'),
    path('add/', views.add_history, name='add'),
    path('load-more/', views.load_more_history, name='load_more'),
]
