from django.urls import path
from .views import collaborative_editor, create_document

app_name = 'collab'

urlpatterns = [
    path('editor/<int:document_id>/', collaborative_editor, name='collaborative_editor'),
    path('create/', create_document, name='create_document'),
]