from rest_framework import serializers
from .models import Photo
from core.serializers import UserSerializer


class PhotoSerializer(serializers.ModelSerializer):
    """照片序列化器"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Photo
        fields = ['id', 'user', 'image', 'description', 'uploaded_at']