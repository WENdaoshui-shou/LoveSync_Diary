from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseForbidden
from django.urls import reverse
from .models import CollaborativeDocument


# 创建文档
@csrf_exempt
@login_required
def create_document(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        document = CollaborativeDocument.objects.create(
            title=data.get('title', '新文档'),
            owner=request.user,
            content=data.get('content', '')
        )
        # 关联情侣（如果存在）
        try:
            profile = request.user.profile
            if profile.couple:
                document.couple = profile
                document.save()
        except:
            pass

        return JsonResponse({
            'id': document.id,
            'title': document.title,
            'content': document.content,
            'url': reverse('collab:collaborative_editor', args=[document.id])
        }, status=201)
    return JsonResponse({'error': 'Method not allowed'}, status=405)
