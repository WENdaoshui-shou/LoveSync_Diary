from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.core.cache import cache
from django.utils import timezone
from django.core.mail import send_mail
import random
import string
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from .models import User, Profile, VerificationCode, VIPMember, VIPPrivilege
from .serializers import UserSerializer, ProfileSerializer, CustomTokenObtainPairSerializer, RegisterSerializer, VIPMemberSerializer, VIPPrivilegeSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    """自定义JWT令牌获取视图"""
    serializer_class = CustomTokenObtainPairSerializer


class RegisterViewSet(viewsets.GenericViewSet):
    """用户注册视图集"""
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """用户注册"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'message': '注册成功',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def send_verification_code(self, request):
        """发送验证码"""
        type = request.data.get('type')  # 'phone' 或 'email'
        target = request.data.get('target')  # 手机号或邮箱
        
        if not type or not target:
            return Response({'message': '缺少必要参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        if type not in ['phone', 'email']:
            return Response({'message': '无效的验证类型'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 生成6位验证码
        code = ''.join(random.choices(string.digits, k=6))
        
        # 设置过期时间为5分钟后
        expires_at = timezone.now() + timezone.timedelta(minutes=5)
        
        # 删除该目标的旧验证码
        VerificationCode.objects.filter(type=type, target=target).delete()
        
        # 创建新验证码
        VerificationCode.objects.create(
            type=type,
            target=target,
            code=code,
            expires_at=expires_at
        )
        
        # 发送验证码（这里使用模拟发送，实际项目中需要集成真实的短信/邮件服务）
        if type == 'phone':
            # 模拟发送短信
            print(f"向手机号 {target} 发送验证码: {code}")
        else:
            # 模拟发送邮件
            print(f"向邮箱 {target} 发送验证码: {code}")
        
        return Response({'message': '验证码发送成功'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def verify_code(self, request):
        """验证验证码"""
        type = request.data.get('type')
        target = request.data.get('target')
        code = request.data.get('code')
        
        if not type or not target or not code:
            return Response({'message': '缺少必要参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 查找未过期且未使用的验证码
            verification_code = VerificationCode.objects.get(
                type=type,
                target=target,
                code=code,
                expires_at__gt=timezone.now(),
                is_used=False
            )
            
            # 标记验证码为已使用
            verification_code.is_used = True
            verification_code.save()
            
            # 更新用户的验证状态
            user = User.objects.get(**{type: target} if type == 'email' else {'username': target})
            if type == 'phone':
                user.phone_verified = True
            else:
                user.email_verified = True
            user.save()
            
            return Response({'message': '验证成功'}, status=status.HTTP_200_OK)
        except VerificationCode.DoesNotExist:
            return Response({'message': '验证码无效或已过期'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'message': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)


class LoginViewSet(viewsets.GenericViewSet):
    """用户登录视图集"""
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """用户登录，获取JWT令牌"""
        print(f"API Login attempt: data={request.data}")
        
        serializer = self.get_serializer(data=request.data)
        
        # 尝试验证，捕获异常并打印详细信息
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            print(f"Serializer validation error: {str(e)}")
            # 打印所有用户，用于调试
            all_users = User.objects.all()
            print(f"All users: {[user.username for user in all_users]}")
            raise
        
        # 获取令牌对
        tokens = serializer.validated_data
        
        # 获取用户信息
        user = serializer.user
        user_data = UserSerializer(user).data
        
        print(f"Login successful for user: {user.username}")
        
        return Response({
            'message': '登录成功',
            'tokens': tokens,
            'user': user_data
        }, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """用户视图集"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的信息"""
        return self.queryset.filter(id=self.request.user.id)


class ProfileViewSet(viewsets.ModelViewSet):
    """用户资料视图集"""
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的资料"""
        return self.queryset.filter(user=self.request.user)


class VIPMemberViewSet(viewsets.ModelViewSet):
    """VIP会员视图集"""
    queryset = VIPMember.objects.all()
    serializer_class = VIPMemberSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的VIP信息"""
        return self.queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """创建VIP会员时自动关联当前用户"""
        serializer.save(user=self.request.user)


class VIPPrivilegeViewSet(viewsets.ModelViewSet):
    """VIP特权视图集"""
    queryset = VIPPrivilege.objects.all()
    serializer_class = VIPPrivilegeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户可用的VIP特权"""
        # 获取当前用户的VIP等级
        user_vip = self.request.user.vip
        # 获取所有当前等级及以下的特权
        return self.queryset.filter(required_level__lte=user_vip.level)


# 首页视图
class IndexView(TemplateView):
    template_name = 'index.html'


# 登录视图
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember-me')  
        verify_code_input = request.POST.get('verify_code')
        
        # 调试信息：打印所有POST数据
        print(f"Login attempt: username={username}, password={password[:3]}..., verify_code={verify_code_input}")
        
        # 验证码验证
        session_code = request.session.get('verify_code')
        if session_code:
            if not verify_code_input:
                messages.error(request, '请输入验证码')
                return redirect('login')
            elif verify_code_input != session_code:
                messages.error(request, '验证码错误')
                return redirect('login')
            
            # 清除session中的验证码
            del request.session['verify_code']
        
        # 直接使用User模型和check_password进行调试
        try:
            # 先检查用户是否存在
            all_users = User.objects.all()
            print(f"All users: {[user.username for user in all_users]}")
            
            # 获取用户对象
            user_obj = User.objects.get(username=username)
            print(f"User found: {user_obj.username}, password_hash={user_obj.password[:20]}...")
            
            # 检查密码是否匹配
            if user_obj.check_password(password):
                print("Password matches!")
                # 直接登录用户
                login(request, user_obj)
                # 根据remember_me设置session过期时间
                if not remember_me:
                    request.session.set_expiry(0)  # 关闭浏览器后失效
                messages.success(request, '登录成功')
                return redirect('community')
            else:
                print("Password does NOT match!")
                # 手动使用Django的密码编码器检查
                from django.contrib.auth.hashers import check_password as django_check_password
                if django_check_password(password, user_obj.password):
                    login(request, user_obj)
                    messages.success(request, '登录成功')
                    return redirect('community')
                else:
                    messages.error(request, '密码错误')
                    return redirect('login')
        except User.DoesNotExist:
            print(f"User not found: {username}")
            messages.error(request, f'未注册')
            return redirect('login')
        except Exception as e:
            print(f"Login error: {e}")
            messages.error(request, f'登录失败: {str(e)}')
            return redirect('login')
    
    return render(request, 'login.html')


# 注册视图
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        name = request.POST.get('name')
        password1 = request.POST.get('password')
        password2 = request.POST.get('confirm-password')
        phone_code = request.POST.get('phone_code')
        
        # 简单的表单验证
        if password1 != password2:
            messages.error(request, '两次密码不一致')
            return redirect('register')
        
        # 实现用户创建逻辑
        try:
            # 首先检查用户名是否已存在
            if User.objects.filter(username=username).exists():
                messages.error(request, '用户名已存在')
                return redirect('register')
            
            # 然后验证验证码
            try:
                verification_code = VerificationCode.objects.get(
                    type='phone',
                    target=username,
                    code=phone_code,
                    expires_at__gt=timezone.now(),
                    is_used=False
                )
            except VerificationCode.DoesNotExist:
                messages.error(request, '手机号验证码无效或已过期')
                return redirect('register')
            
            # 创建用户 - 直接使用create方法并手动加密密码
            from django.contrib.auth.hashers import make_password
            user = User.objects.create(
                username=username,
                email=email,
                name=name,
                password=make_password(password1),
                phone_verified=True
            )
            
            # 标记验证码为已使用
            verification_code.is_used = True
            verification_code.save()
            
            messages.success(request, '注册成功，请登录')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'注册失败: {str(e)}')
            return redirect('register')
    
    return render(request, 'register.html')


# 登出视图
def logout_view(request):
    logout(request)
    messages.success(request, '已成功登出')
    return redirect('login')








# 个人中心视图
@login_required
def personal_center_view(request):
    return render(request, 'personal_center.html')


# 消息视图
@login_required
def message_view(request):
    return render(request, 'message.html')








# 设置视图
@login_required
def settings_view(request, setting_type=None):
    if request.method == 'POST':
        try:
            profile = request.user.profile
            
            # 处理个人信息设置
            if setting_type == 'profile':
                # 获取表单数据
                name = request.POST.get('name')
                gender = request.POST.get('gender')
                birth_date = request.POST.get('birth_date')
                location = request.POST.get('location')
                bio = request.POST.get('bio')
                
                # 处理头像上传
                user_avatar = request.FILES.get('userAvatar')
                
                # 更新用户信息
                request.user.name = name
                request.user.save()
                
                # 更新用户Profile
                if profile:
                    # 更新基本信息
                    profile.gender = gender
                    if birth_date:
                        profile.birth_date = birth_date
                    profile.location = location
                    profile.bio = bio
                    
                    # 更新头像
                    if user_avatar:
                        profile.userAvatar = user_avatar
                    
                    # 保存Profile
                    profile.save()
                
                messages.success(request, '个人信息更新成功')
            # 处理通知设置
            elif setting_type == 'notifications':
                # 获取表单数据
                profile.notification_sound = request.POST.get('notification_sound') == 'on'
                profile.notification_vibration = request.POST.get('notification_vibration') == 'on'
                profile.do_not_disturb = request.POST.get('do_not_disturb') == 'on'
                profile.couple_messages = request.POST.get('couple_messages') == 'on'
                profile.community_messages = request.POST.get('community_messages') == 'on'
                profile.system_messages = request.POST.get('system_messages') == 'on'
                profile.comments_replies = request.POST.get('comments_replies') == 'on'
                profile.likes_favorites = request.POST.get('likes_favorites') == 'on'
                profile.anniversary_reminders = request.POST.get('anniversary_reminders') == 'on'
                profile.couple_activity_recommendations = request.POST.get('couple_activity_recommendations') == 'on'
                profile.hot_topic_reminders = request.POST.get('hot_topic_reminders') == 'on'
                profile.promotion_push = request.POST.get('promotion_push') == 'on'
                
                profile.save()
                messages.success(request, '通知设置更新成功')
            # 处理隐私设置
            elif setting_type == 'privacy':
                # 获取表单数据
                profile.profile_visibility = request.POST.get('profile_visibility', 'everyone')
                profile.show_online_status = request.POST.get('show_online_status') == 'on'
                profile.allow_search = request.POST.get('allow_search') == 'on'
                profile.show_location = request.POST.get('show_location') == 'on'
                profile.moments_visibility = request.POST.get('moments_visibility', 'everyone')
                profile.album_visibility = request.POST.get('album_visibility', 'friends')
                
                profile.save()
                messages.success(request, '隐私设置更新成功')
            # 处理账号安全设置
            elif setting_type == 'account':
                # 获取表单数据
                profile.two_factor_auth = request.POST.get('two_factor_auth') == 'on'
                profile.login_notification = request.POST.get('login_notification') == 'on'
                profile.session_management = request.POST.get('session_management') == 'on'
                
                profile.save()
                messages.success(request, '账号安全设置更新成功')
            # 处理外观设置
            elif setting_type == 'appearance':
                # 获取表单数据
                profile.theme = request.POST.get('theme', 'light')
                profile.font_size = request.POST.get('font_size', 'medium')
                profile.interface_style = request.POST.get('interface_style', 'modern')
                
                profile.save()
                messages.success(request, '外观设置更新成功')
        except Exception as e:
            messages.error(request, f'设置更新失败: {str(e)}')
        
        return redirect('settings', setting_type=setting_type)
    
    return render(request, 'settings.html', {'setting_type': setting_type})


# 验证码生成视图
def verify_code(request):
    """生成验证码图片"""
    # 生成4位随机验证码
    code = ''.join(random.choices('0123456789', k=4))
    
    # 将验证码存储到session中
    request.session['verify_code'] = code
    
    # 创建验证码图片
    width, height = 120, 40
    image = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # 绘制干扰线
    for _ in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line((x1, y1, x2, y2), fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), width=1)
    
    # 绘制验证码文本
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype('arial.ttf', 24)
    except:
        # 如果系统字体不可用，使用默认字体
        font = ImageFont.load_default()
    
    # 绘制每个字符
    for i, char in enumerate(code):
        x = 20 + i * 20
        y = random.randint(5, 15)
        draw.text((x, y), char, font=font, fill=(random.randint(0, 100), random.randint(0, 100), random.randint(0, 100)))
    
    # 保存图片到内存
    buffer = BytesIO()
    image.save(buffer, 'PNG')
    buffer.seek(0)
    
    # 返回图片响应
    return HttpResponse(buffer.getvalue(), content_type='image/png')


# 删除账号视图
@login_required
def delete_account(request):
    """删除账号"""
    if request.method == 'POST':
        try:
            # 获取当前用户
            user = request.user
            
            # 删除用户相关的所有数据
            # 这里会自动级联删除相关模型（如Profile、VIPMember等）
            user.delete()
            
            # 登出用户
            logout(request)
            
            messages.success(request, '账号已成功删除')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'删除账号失败: {str(e)}')
            return redirect('couple')
    
    # 如果不是POST请求，重定向到情侣页面
    return redirect('couple')
