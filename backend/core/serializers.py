from rest_framework import serializers
from .models import User, Profile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'email']


class ProfileSerializer(serializers.ModelSerializer):
    """用户资料序列化器"""
    user = UserSerializer(read_only=True)
    couple = serializers.SerializerMethodField()
    
    def get_couple(self, obj):
        """获取情侣信息"""
        if obj.couple:
            return ProfileSerializer(obj.couple, fields=['id', 'user', 'userAvatar', 'couple_joined_at']).data
        return None
    
    class Meta:
        model = Profile
        fields = ['id', 'user', 'userAvatar', 'gender', 'birth_date', 'location', 'bio', 'couple', 'couple_code', 'couple_joined_at']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """自定义JWT令牌获取序列化器"""
    
    # 允许使用username或phone作为登录字段
    username_field = 'username'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 允许前端使用phone或username字段登录
        self.fields['username'] = serializers.CharField(required=True)
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # 添加自定义声明
        token['username'] = user.username
        token['name'] = user.name
        
        return token
    
    def validate(self, attrs):
        # 尝试使用用户名或手机号登录
        username = attrs.get('username')
        password = attrs.get('password')
        
        # 确保username和password都存在
        if not username or not password:
            raise serializers.ValidationError('必须提供用户名和密码')
        
        # 查找用户，支持使用username登录
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError('未注册')
        
        # 检查密码是否正确
        if not user.check_password(password):
            raise serializers.ValidationError('密码错误')
        
        # 设置用户对象，以便后续使用
        self.user = user
        
        # 调用父类方法生成令牌
        data = super().validate(attrs)
        
        # 添加用户信息到响应
        data['user'] = UserSerializer(self.user).data
        
        return data


class RegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'password', 'name', 'email']
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def create(self, validated_data):
        """创建用户"""
        user = User.objects.create(
            username=validated_data['username'],
            name=validated_data['name'],
            email=validated_data.get('email', ''),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user



