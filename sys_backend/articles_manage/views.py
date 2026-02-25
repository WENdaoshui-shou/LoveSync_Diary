from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime

# 官方专栏管理 API

@csrf_exempt
def get_columns(request):
    """获取官方专栏列表"""
    if request.method == 'GET':
        try:
            from sys_LoveSync.storage import AliyunOSSStorage
            storage = AliyunOSSStorage()
            
            with connection.cursor() as cursor:
                # 使用 SQL 语句获取专栏列表
                cursor.execute('''
                    SELECT id, name, slug, description, cover_image, category, subscriber_count, view_count, is_active, updated_at
                    FROM articles_officialcolumn
                    ORDER BY updated_at DESC
                ''')
                columns = cursor.fetchall()
                
                # 处理结果
                column_list = []
                for column in columns:
                    cover_image = column[4]
                    cover_image_url = storage.url(cover_image) if cover_image else None
                    
                    column_list.append({
                        'id': column[0],
                        'name': column[1],
                        'slug': column[2],
                        'description': column[3],
                        'cover_image': cover_image_url,
                        'category': column[5],
                        'subscriber_count': column[6],
                        'view_count': column[7],
                        'is_active': column[8],
                        'updated_at': column[9].strftime('%Y-%m-%d %H:%M:%S') if column[9] else None
                    })
                
                return JsonResponse({'success': True, 'data': column_list}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@csrf_exempt
def get_column_detail(request, column_id):
    """获取官方专栏详情"""
    if request.method == 'GET':
        try:
            from sys_LoveSync.storage import AliyunOSSStorage
            storage = AliyunOSSStorage()
            
            with connection.cursor() as cursor:
                # 使用 SQL 语句获取专栏详情
                cursor.execute('''
                    SELECT id, name, slug, description, cover_image, category, subscriber_count, view_count, is_active, updated_at
                    FROM articles_officialcolumn
                    WHERE id = %s
                ''', [column_id])
                column = cursor.fetchone()
                
                if not column:
                    return JsonResponse({'success': False, 'error': 'Column not found'}, status=404)
                
                # 处理结果
                cover_image = column[4]
                cover_image_url = storage.url(cover_image) if cover_image else None
                
                column_data = {
                    'id': column[0],
                    'name': column[1],
                    'slug': column[2],
                    'description': column[3],
                    'cover_image': cover_image_url,
                    'category': column[5],
                    'subscriber_count': column[6],
                    'view_count': column[7],
                    'is_active': column[8],
                    'updated_at': column[9].strftime('%Y-%m-%d %H:%M:%S') if column[9] else None
                }
                
                return JsonResponse({'success': True, 'data': column_data}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@csrf_exempt
def create_column(request):
    """创建官方专栏"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            with connection.cursor() as cursor:
                # 使用 SQL 语句创建专栏（MySQL 兼容方式）
                cursor.execute('''
                    INSERT INTO articles_officialcolumn (name, slug, description, cover_image, category, subscriber_count, view_count, is_active, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', [
                    data.get('name'),
                    data.get('slug'),
                    data.get('description'),
                    data.get('cover_image'),
                    data.get('category'),
                    data.get('subscriber_count', 0),
                    data.get('view_count', 0),
                    data.get('is_active', True),
                    datetime.now()
                ])
                # 使用 LAST_INSERT_ID() 获取最后插入的ID
                cursor.execute('SELECT LAST_INSERT_ID()')
                column_id = cursor.fetchone()[0]
                
                return JsonResponse({'success': True, 'data': {'id': column_id}}, status=201)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@csrf_exempt
def update_column(request, column_id):
    """更新官方专栏"""
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            
            with connection.cursor() as cursor:
                # 使用 SQL 语句更新专栏
                cursor.execute('''
                    UPDATE articles_officialcolumn
                    SET name = %s, slug = %s, description = %s, cover_image = %s, category = %s, is_active = %s, updated_at = %s
                    WHERE id = %s
                ''', [
                    data.get('name'),
                    data.get('slug'),
                    data.get('description'),
                    data.get('cover_image'),
                    data.get('category'),
                    data.get('is_active'),
                    datetime.now(),
                    column_id
                ])
                
                if cursor.rowcount == 0:
                    return JsonResponse({'success': False, 'error': 'Column not found'}, status=404)
                
                return JsonResponse({'success': True, 'message': 'Column updated successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@csrf_exempt
def delete_column(request, column_id):
    """删除官方专栏"""
    if request.method == 'DELETE':
        try:
            with connection.cursor() as cursor:
                # 使用 SQL 语句删除专栏
                cursor.execute('''
                    DELETE FROM articles_officialcolumn
                    WHERE id = %s
                ''', [column_id])
                
                if cursor.rowcount == 0:
                    return JsonResponse({'success': False, 'error': 'Column not found'}, status=404)
                
                return JsonResponse({'success': True, 'message': 'Column deleted successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

# 专栏文章管理 API

@csrf_exempt
def get_articles(request):
    """获取专栏文章列表"""
    if request.method == 'GET':
        try:
            from sys_LoveSync.storage import AliyunOSSStorage
            storage = AliyunOSSStorage()
            
            with connection.cursor() as cursor:
                # 使用 SQL 语句获取文章列表
                cursor.execute('''
                    SELECT id, column_id, title, content, cover_image, view_count, like_count, comment_count, published_at, updated_at
                    FROM articles_columnarticle
                    ORDER BY published_at DESC
                ''')
                articles = cursor.fetchall()
                
                # 处理结果
                article_list = []
                for article in articles:
                    cover_image = article[4]
                    cover_image_url = storage.url(cover_image) if cover_image else None
                    
                    article_list.append({
                        'id': article[0],
                        'column_id': article[1],
                        'title': article[2],
                        'content': article[3],
                        'cover_image': cover_image_url,
                        'view_count': article[5],
                        'like_count': article[6],
                        'comment_count': article[7],
                        'published_at': article[8].strftime('%Y-%m-%d %H:%M:%S') if article[8] else None,
                        'updated_at': article[9].strftime('%Y-%m-%d %H:%M:%S') if article[9] else None
                    })
                
                return JsonResponse({'success': True, 'data': article_list}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@csrf_exempt
def get_article_detail(request, article_id):
    """获取专栏文章详情"""
    if request.method == 'GET':
        try:
            from sys_LoveSync.storage import AliyunOSSStorage
            storage = AliyunOSSStorage()
            
            with connection.cursor() as cursor:
                # 使用 SQL 语句获取文章详情
                cursor.execute('''
                    SELECT id, column_id, title, content, cover_image, view_count, like_count, comment_count, published_at, updated_at
                    FROM articles_columnarticle
                    WHERE id = %s
                ''', [article_id])
                article = cursor.fetchone()
                
                if not article:
                    return JsonResponse({'success': False, 'error': 'Article not found'}, status=404)
                
                # 处理结果
                cover_image = article[4]
                cover_image_url = storage.url(cover_image) if cover_image else None
                
                article_data = {
                    'id': article[0],
                    'column_id': article[1],
                    'title': article[2],
                    'content': article[3],
                    'cover_image': cover_image_url,
                    'view_count': article[5],
                    'like_count': article[6],
                    'comment_count': article[7],
                    'published_at': article[8].strftime('%Y-%m-%d %H:%M:%S') if article[8] else None,
                    'updated_at': article[9].strftime('%Y-%m-%d %H:%M:%S') if article[9] else None
                }
                
                return JsonResponse({'success': True, 'data': article_data}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@csrf_exempt
def create_article(request):
    """创建专栏文章"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            with connection.cursor() as cursor:
                # 使用 SQL 语句创建文章（MySQL 兼容方式）
                cursor.execute('''
                    INSERT INTO articles_columnarticle (column_id, title, content, cover_image, view_count, like_count, comment_count, published_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', [
                    data.get('column_id'),
                    data.get('title'),
                    data.get('content'),
                    data.get('cover_image'),
                    data.get('view_count', 0),
                    data.get('like_count', 0),
                    data.get('comment_count', 0),
                    datetime.now(),
                    datetime.now()
                ])
                # 使用 LAST_INSERT_ID() 获取最后插入的ID
                cursor.execute('SELECT LAST_INSERT_ID()')
                article_id = cursor.fetchone()[0]
                
                return JsonResponse({'success': True, 'data': {'id': article_id}}, status=201)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@csrf_exempt
def update_article(request, article_id):
    """更新专栏文章"""
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            
            with connection.cursor() as cursor:
                # 使用 SQL 语句更新文章
                cursor.execute('''
                    UPDATE articles_columnarticle
                    SET column_id = %s, title = %s, content = %s, cover_image = %s, updated_at = %s
                    WHERE id = %s
                ''', [
                    data.get('column_id'),
                    data.get('title'),
                    data.get('content'),
                    data.get('cover_image'),
                    datetime.now(),
                    article_id
                ])
                
                if cursor.rowcount == 0:
                    return JsonResponse({'success': False, 'error': 'Article not found'}, status=404)
                
                return JsonResponse({'success': True, 'message': 'Article updated successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@csrf_exempt
def delete_article(request, article_id):
    """删除专栏文章"""
    if request.method == 'DELETE':
        try:
            with connection.cursor() as cursor:
                # 使用 SQL 语句删除文章
                cursor.execute('''
                    DELETE FROM articles_columnarticle
                    WHERE id = %s
                ''', [article_id])
                
                if cursor.rowcount == 0:
                    return JsonResponse({'success': False, 'error': 'Article not found'}, status=404)
                
                return JsonResponse({'success': True, 'message': 'Article deleted successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

# 专栏评论管理 API

@csrf_exempt
def get_comments(request):
    """获取专栏评论列表"""
    if request.method == 'GET':
        try:
            with connection.cursor() as cursor:
                # 使用 SQL 语句获取评论列表
                cursor.execute('''
                    SELECT id, article_id, user_id, content, like_count, created_at, updated_at
                    FROM articles_columncomment
                    ORDER BY created_at DESC
                ''')
                comments = cursor.fetchall()
                
                # 处理结果
                comment_list = []
                for comment in comments:
                    comment_list.append({
                        'id': comment[0],
                        'article_id': comment[1],
                        'user_id': comment[2],
                        'content': comment[3],
                        'like_count': comment[4],
                        'created_at': comment[5].strftime('%Y-%m-%d %H:%M:%S') if comment[5] else None,
                        'updated_at': comment[6].strftime('%Y-%m-%d %H:%M:%S') if comment[6] else None
                    })
                
                return JsonResponse({'success': True, 'data': comment_list}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@csrf_exempt
def delete_comment(request, comment_id):
    """删除专栏评论"""
    if request.method == 'DELETE':
        try:
            with connection.cursor() as cursor:
                # 使用 SQL 语句删除评论
                cursor.execute('''
                    DELETE FROM articles_columncomment
                    WHERE id = %s
                ''', [comment_id])
                
                if cursor.rowcount == 0:
                    return JsonResponse({'success': False, 'error': 'Comment not found'}, status=404)
                
                return JsonResponse({'success': True, 'message': 'Comment deleted successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

# 专栏订阅管理 API

@csrf_exempt
def get_subscriptions(request):
    """获取专栏订阅列表"""
    if request.method == 'GET':
        try:
            with connection.cursor() as cursor:
                # 使用 SQL 语句获取订阅列表
                cursor.execute('''
                    SELECT id, user_id, column_id, is_subscribed, created_at, updated_at
                    FROM articles_columnsubscription
                    ORDER BY created_at DESC
                ''')
                subscriptions = cursor.fetchall()
                
                # 处理结果
                subscription_list = []
                for subscription in subscriptions:
                    subscription_list.append({
                        'id': subscription[0],
                        'user_id': subscription[1],
                        'column_id': subscription[2],
                        'is_subscribed': subscription[3],
                        'created_at': subscription[4].strftime('%Y-%m-%d %H:%M:%S') if subscription[4] else None,
                        'updated_at': subscription[5].strftime('%Y-%m-%d %H:%M:%S') if subscription[5] else None
                    })
                
                return JsonResponse({'success': True, 'data': subscription_list}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

# 文章点赞管理 API

@csrf_exempt
def get_likes(request):
    """获取文章点赞列表"""
    if request.method == 'GET':
        try:
            with connection.cursor() as cursor:
                # 使用 SQL 语句获取点赞列表
                cursor.execute('''
                    SELECT id, article_id, user_id, created_at
                    FROM articles_articlelike
                    ORDER BY created_at DESC
                ''')
                likes = cursor.fetchall()
                
                # 处理结果
                like_list = []
                for like in likes:
                    like_list.append({
                        'id': like[0],
                        'article_id': like[1],
                        'user_id': like[2],
                        'created_at': like[3].strftime('%Y-%m-%d %H:%M:%S') if like[3] else None
                    })
                
                return JsonResponse({'success': True, 'data': like_list}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@csrf_exempt
def get_statistics(request):
    """获取文章统计数据"""
    if request.method == 'GET':
        try:
            with connection.cursor() as cursor:
                # 获取总文章数
                cursor.execute('SELECT COUNT(*) FROM articles_columnarticle')
                total_articles = cursor.fetchone()[0] or 0
                
                # 获取总专栏数
                cursor.execute('SELECT COUNT(*) FROM articles_officialcolumn')
                total_columns = cursor.fetchone()[0] or 0
                
                # 获取总浏览量
                cursor.execute('SELECT SUM(view_count) FROM articles_columnarticle')
                total_views = cursor.fetchone()[0] or 0
                
                # 获取总点赞数
                cursor.execute('SELECT SUM(like_count) FROM articles_columnarticle')
                total_likes = cursor.fetchone()[0] or 0
                
                # 获取总评论数
                cursor.execute('SELECT SUM(comment_count) FROM articles_columnarticle')
                total_comments = cursor.fetchone()[0] or 0
                
                # 获取总订阅数
                cursor.execute('SELECT COUNT(*) FROM articles_columnsubscription WHERE is_subscribed = TRUE')
                total_subscriptions = cursor.fetchone()[0] or 0
                
                return JsonResponse({
                    'success': True,
                    'data': {
                        'total_articles': total_articles,
                        'total_columns': total_columns,
                        'total_views': total_views,
                        'total_likes': total_likes,
                        'total_comments': total_comments,
                        'total_subscriptions': total_subscriptions
                    }
                }, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

