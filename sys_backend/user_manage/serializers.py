from rest_framework import serializers
from django.contrib.auth import get_user_model
from datetime import datetime

User = get_user_model()


class UserListSerializer(serializers.ModelSerializer):
    """用户列表序列化器"""
    create_time = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'email', 'is_active', 'create_time', 'status_display']
        
    def get_create_time(self, obj):
        """格式化创建时间"""
        if hasattr(obj, 'date_joined'):
            return obj.date_joined.strftime('%Y-%m-%d %H:%M:%S')
        return None
        
    def get_status_display(self, obj):
        """获取状态显示文本"""
        return "启用" if obj.is_active else "禁用"
        
    def get_name(self, obj):
        """获取用户姓名"""
        return getattr(obj, 'name', obj.username)


class UserDetailSerializer(serializers.ModelSerializer):
    """用户详情序列化器"""
    create_time = serializers.SerializerMethodField()
    last_login_time = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    phone_verified = serializers.SerializerMethodField()
    email_verified = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'name',
            'is_active', 'is_staff', 'is_superuser', 'date_joined',
            'last_login', 'create_time', 'last_login_time', 'status_display',
            'phone_verified', 'email_verified'
        ]
        
    def get_create_time(self, obj):
        """格式化创建时间"""
        if hasattr(obj, 'date_joined'):
            return obj.date_joined.strftime('%Y-%m-%d %H:%M:%S')
        return None
        
    def get_last_login_time(self, obj):
        """格式化最后登录时间"""
        if obj.last_login:
            return obj.last_login.strftime('%Y-%m-%d %H:%M:%S')
        return "从未登录"
        
    def get_status_display(self, obj):
        """获取状态显示文本"""
        if obj.is_superuser:
            return "超级管理员"
        elif obj.is_staff:
            return "管理员"
        elif obj.is_active:
            return "正常用户"
        else:
            return "已禁用"
    
    def get_phone_verified(self, obj):
        """获取手机号验证状态"""
        return getattr(obj, 'phone_verified', False)
    
    def get_email_verified(self, obj):
        """获取邮箱验证状态"""
        return getattr(obj, 'email_verified', False)


class UserStatusUpdateSerializer(serializers.ModelSerializer):
    """用户状态更新序列化器"""
    
    class Meta:
        model = User
        fields = ['is_active']
        
    def validate_is_active(self, value):
        """验证状态值"""
        if not isinstance(value, bool):
            raise serializers.ValidationError("状态必须是布尔值")
        return value