from rest_framework import serializers
from .models import Note, NoteImage
from core.serializers import UserSerializer


class NoteImageSerializer(serializers.ModelSerializer):
    """日记图片序列化器"""
    class Meta:
        model = NoteImage
        fields = ['id', 'noteimage']


class NoteSerializer(serializers.ModelSerializer):
    """日记序列化器"""
    user = UserSerializer(read_only=True)
    note_images = NoteImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Note
        fields = ['id', 'user', 'context', 'created_at', 'mood', 'is_shared', 'likes', 'comments', 'note_images']
    
    def create(self, validated_data):
        """创建日记"""
        images_data = self.context['request'].FILES.getlist('images')
        
        note = Note.objects.create(**validated_data)
        
        # 处理图片
        for image_data in images_data:
            NoteImage.objects.create(notemoment=note, noteimage=image_data)
        
        return note
    
    def to_representation(self, instance):
        """自定义序列化输出"""
        representation = super().to_representation(instance)
        
        # 添加心情相关的自定义字段
        representation['mood_color'] = instance.get_mood_color()
        representation['mood_icon'] = instance.get_mood_icon()
        representation['mood_display_text'] = instance.get_mood_display_text()
        representation['mood_css_class'] = instance.get_mood_css_class()
        
        return representation