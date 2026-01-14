from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseForbidden
from django.urls import reverse
from .models import CollaborativeDocument


# 协作编辑器页面
@login_required
def collaborative_editor(request, document_id):
    document = get_object_or_404(CollaborativeDocument, id=document_id)

    # 检查权限：只有文档所有者或其情侣可以访问
    if request.user != document.owner and (document.couple is None or request.user != document.couple.user):
        return HttpResponseForbidden("你无权访问此文档")

    return render(request, 'collaborative_editor.html', {
        'document': document
    })


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
            'url': reverse('collaborative_editor', args=[document.id])
        }, status=201)
    return JsonResponse({'error': 'Method not allowed'}, status=405)
