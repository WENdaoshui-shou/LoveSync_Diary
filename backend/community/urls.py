from django.urls import path
from .views import create_report

app_name = 'community'

urlpatterns = [
    path('api/reports/create/', create_report, name='create_report'),
]