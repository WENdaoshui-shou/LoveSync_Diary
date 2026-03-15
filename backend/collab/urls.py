from django.urls import path
from .views import  create_document

app_name = 'collab'

urlpatterns = [
    path('create/', create_document, name='create_document'),
]