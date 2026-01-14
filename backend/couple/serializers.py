from rest_framework import serializers
from .models import Anniversary, CoupleTask, TaskCompletion


class AnniversarySerializer(serializers.ModelSerializer):
    """纪念日序列化器"""
    class Meta:
        model = Anniversary
        fields = ['id', 'title', 'anniversary_date', 'anniversary_type', 'description', 'is_reminder_enabled', 'reminder_days', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class CoupleTaskSerializer(serializers.ModelSerializer):
    """情侣任务序列化器"""
    class Meta:
        model = CoupleTask
        fields = ['id', 'title', 'description', 'deadline', 'status', 'is_shared', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class TaskCompletionSerializer(serializers.ModelSerializer):
    """任务完成记录序列化器"""
    class Meta:
        model = TaskCompletion
        fields = ['id', 'task', 'user', 'is_completed', 'completed_at', 'created_at']
        read_only_fields = ['created_at']