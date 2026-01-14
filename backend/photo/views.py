from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from django.http import JsonResponse, HttpResponse, Http404, HttpResponseForbidden
from django.conf import settings
from django.core.exceptions import PermissionDenied
import os
from moment.models import Moment
from .models import Photo
from .serializers import PhotoSerializer


class PhotoViewSet(viewsets.ModelViewSet):
    """照片视图集"""
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取照片列表，支持按用户筛选"""
        queryset = self.queryset.order_by('-uploaded_at')
        user_id = self.request.query_params.get('user_id')
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        else:
            # 默认只显示当前用户的照片
            queryset = queryset.filter(user=self.request.user)
        
        return queryset
    
    def perform_create(self, serializer):
        """创建照片"""
        serializer.save(user=self.request.user)


# 相册页面
@login_required
def photo_album(request):
    if request.method == 'GET':
        user = request.user

        print(f"用户ID: {user.id}")
        print(f"头像路径: {user.profile.userAvatar}")

        moment = Moment.objects.filter(user=request.user).select_related('user__profile').order_by('-created_at')
        photo = Photo.objects.filter(user=request.user).order_by('-uploaded_at')

        return render(request, 'photo_album.html', {
            'user': request.user,
            'moments': moment,
            'photos': photo,
        })

    if request.method == 'POST':
        # 处理照片上传
        description = request.POST.get('description', '').strip()
        images = request.FILES.getlist('images')  # 获取上传的图片（多张）

        photos = Photo.objects.filter(user=request.user).order_by('-uploaded_at')

        # 验证至少上传了一张图片
        if not images:
            return render(request, 'photo_album.html', {
                'error': '请选择至少一张图片上传',
                'photos': photos
            })

        try:
            # 为每张上传的图片创建Photo对象
            for image in images:
                Photo.objects.create(
                    user=request.user,
                    image=image,
                    description=description,
                )

            return redirect('photo_album')

        except Exception as e:
            return render(request, 'photo_album.html', {
                'error': f'上传失败: {str(e)}',
                'photos': photos
            })


# 删除照片
@login_required
@require_http_methods(['DELETE', 'POST'])
def delete_photo(request, photo_id):
    # 获取当前用户的照片对象，不存在或非所有者则返回404
    photo = get_object_or_404(Photo, id=photo_id, user=request.user)

    try:
        # 删除照片文件
        if photo.image:
            photo.image.delete(save=False)  # 先删除物理文件

        # 删除数据库记录
        photo.delete()

        return JsonResponse({'status': 'success', 'message': '照片删除成功'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# 照片下载
@login_required
def download_photo(request, photo_id):
    """处理照片下载请求"""
    # 获取照片对象
    photo = get_object_or_404(Photo, id=photo_id)

    # 权限检查（确保用户有权限下载）
    # 1. 照片所有者
    # 2. 已共享给伴侣的照片
    if photo.user != request.user and not photo.is_shared_with_partner(request.user):
        raise PermissionDenied("你没有权限下载这张照片")

    # 获取照片文件路径
    file_path = os.path.join(settings.MEDIA_ROOT, str(photo.image))

    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise Http404("照片文件不存在")

    # 读取文件内容
    with open(file_path, 'rb') as f:
        file_content = f.read()

    # 构建响应
    response = HttpResponse(file_content, content_type='image/jpeg')

    # 设置下载文件名（使用原始文件名或自定义）
    original_filename = os.path.basename(photo.image.name)
    response['Content-Disposition'] = f'attachment; filename="{original_filename}"'

    # 设置文件大小
    response['Content-Length'] = os.path.getsize(file_path)

    return response