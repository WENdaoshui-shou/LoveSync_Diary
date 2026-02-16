from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from datetime import datetime
from django.db import connection

@csrf_exempt
@login_required
def create_report(request):
    """创建举报"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            reporter_id = request.user.id
            reported_user_id = data.get('reported_user')
            
            if not reported_user_id:
                return JsonResponse({'error': '请提供被举报人信息'}, status=400)
            
            # 验证被举报人是否存在
            check_sql = "SELECT id FROM core_user WHERE id = %s"
            with connection.cursor() as cursor:
                cursor.execute(check_sql, [reported_user_id])
                if not cursor.fetchone():
                    return JsonResponse({'error': '被举报人不存在'}, status=400)
            
            sql = """
                INSERT INTO community_report (
                    reporter_id, reported_user_id, report_type, title, description,
                    evidence, status, priority, is_urgent, content_type, content_id,
                    content_title, created_at, reviewed_at, resolved_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NULL, NULL)
            """
            
            params = [
                reporter_id,
                reported_user_id,
                data.get('report_type', 'other'),
                data.get('title', ''),
                data.get('description', ''),
                data.get('evidence', ''),
                'pending',
                data.get('priority', 1),
                data.get('is_urgent', False),
                data.get('content_type', None),
                data.get('content_id', None),
                data.get('content_title', '')
            ]
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                report_id = cursor.lastrowid
            
            # 返回成功响应
            return JsonResponse({'id': report_id, 'message': '举报提交成功'}, status=201)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': '方法不允许'}, status=405)