from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from django.db import connection
from django.contrib.auth import get_user_model

User = get_user_model()


class MomentViewSet(viewsets.ViewSet):
    """动态管理视图集 - 使用SQL操作"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def list(self, request):
        """获取动态列表"""
        try:
            # 获取查询参数
            search = request.query_params.get('search', '')
            user_id = request.query_params.get('user_id', '')
            is_shared = request.query_params.get('is_shared', '')
            status = request.query_params.get('status', '')
            date_range = request.query_params.get('date_range', '')
            hot = request.query_params.get('hot', '')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            # 构建基础SQL查询
            sql = """
                SELECT 
                    m.id,
                    m.content,
                    m.likes,
                    m.comments,
                    m.favorites,
                    m.view_count,
                    m.created_at,
                    m.is_shared,
                    u.name,
                    u.email
                FROM moment_moment m
                INNER JOIN core_user u ON m.user_id = u.id
                WHERE 1=1
            """
            
            params = []
            
            # 添加搜索条件
            if search:
                sql += " AND (m.content LIKE %s OR u.username LIKE %s)"
                search_param = f"%{search}%"
                params.extend([search_param, search_param])
            
            # 添加用户筛选
            if user_id:
                sql += " AND m.user_id = %s"
                params.append(int(user_id))
            
            # 添加分享状态筛选
            if is_shared in ['true', 'false']:
                sql += " AND m.is_shared = %s"
                params.append(is_shared == 'true')
            
            # 添加排序
            if hot:
                sql += " ORDER BY m.likes DESC, m.created_at DESC"
            else:
                sql += " ORDER BY m.created_at DESC"
            
            # 获取总数
            count_sql = sql.replace("SELECT m.id, m.content, m.likes, m.comments, m.favorites, m.view_count, m.created_at, m.is_shared, u.name, u.email", "SELECT COUNT(*)")
            with connection.cursor() as cursor:
                cursor.execute(count_sql, params)
                total = cursor.fetchone()[0]
            
            # 添加分页
            offset = (page - 1) * page_size
            sql += " LIMIT %s OFFSET %s"
            params.extend([page_size, offset])
            
            # 执行查询
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                moments = []
                for row in cursor.fetchall():
                    moment = dict(zip(columns, row))
                    moments.append(moment)
            
            return Response({
                'count': total,
                'results': moments,
                'next': None if page * page_size >= total else f'?page={page + 1}',
                'previous': None if page <= 1 else f'?page={page - 1}'
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, pk=None):
        """获取单个动态详情"""
        try:
            sql = """
                SELECT 
                    m.id,
                    m.content,
                    m.likes,
                    m.comments,
                    m.favorites,
                    m.view_count,
                    m.created_at,
                    m.is_shared,
                    u.username,
                    u.email
                FROM moment_moment m
                INNER JOIN core_user u ON m.user_id = u.id
                WHERE m.id = %s
            """
            
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                result = cursor.fetchone()
                
            if result:
                columns = ['id', 'content', 'likes', 'comments', 'favorites', 'view_count', 'created_at', 'is_shared', 'username', 'email']
                moment = dict(zip(columns, result))
                return Response(moment)
            else:
                return Response({
                    'error': '动态不存在'
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, pk=None):
        """删除动态"""
        try:
            # 首先删除相关的图片
            delete_images_sql = "DELETE FROM moment_momentimage WHERE moment_id = %s"
            with connection.cursor() as cursor:
                cursor.execute(delete_images_sql, [pk])
            
            # 删除相关的标签关联
            delete_tags_sql = "DELETE FROM moment_moment_tags WHERE moment_id = %s"
            with connection.cursor() as cursor:
                cursor.execute(delete_tags_sql, [pk])
            
            # 删除相关的点赞
            delete_likes_sql = "DELETE FROM moment_like WHERE moment_id = %s"
            with connection.cursor() as cursor:
                cursor.execute(delete_likes_sql, [pk])
            
            # 先删除所有评论点赞（避免外键约束）
            delete_all_comment_likes_sql = """
                DELETE FROM moment_commentlike 
                WHERE comment_id IN (SELECT id FROM moment_comment WHERE moment_id = %s)
            """
            with connection.cursor() as cursor:
                cursor.execute(delete_all_comment_likes_sql, [pk])
            
            # 先删除所有子评论（parent_id不为NULL的评论）
            delete_child_comments_sql = """
                DELETE FROM moment_comment 
                WHERE moment_id = %s AND parent_id IS NOT NULL
            """
            with connection.cursor() as cursor:
                cursor.execute(delete_child_comments_sql, [pk])
            
            # 再删除所有主评论（parent_id为NULL的评论）
            delete_parent_comments_sql = """
                DELETE FROM moment_comment 
                WHERE moment_id = %s AND parent_id IS NULL
            """
            with connection.cursor() as cursor:
                cursor.execute(delete_parent_comments_sql, [pk])
            
            # 最后删除动态
            delete_moment_sql = "DELETE FROM moment_moment WHERE id = %s"
            with connection.cursor() as cursor:
                cursor.execute(delete_moment_sql, [pk])
            
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def toggle_share(self, request, pk=None):
        """切换分享状态"""
        try:
            # 获取当前分享状态
            sql = "SELECT is_shared FROM moment_moment WHERE id = %s"
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                result = cursor.fetchone()
                
            if not result:
                return Response({
                    'error': '动态不存在'
                }, status=status.HTTP_404_NOT_FOUND)
            
            current_shared = result[0]
            new_shared = not current_shared
            
            # 更新分享状态
            update_sql = "UPDATE moment_moment SET is_shared = %s WHERE id = %s"
            with connection.cursor() as cursor:
                cursor.execute(update_sql, [new_shared, pk])
            
            return Response({
                'is_shared': new_shared,
                'message': '分享状态已更新'
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取动态统计数据"""
        try:
            # 总动态数
            total_sql = "SELECT COUNT(*) FROM moment_moment"
            
            # 总点赞数
            total_likes_sql = "SELECT SUM(likes) FROM moment_moment"
            
            # 总评论数
            total_comments_sql = "SELECT SUM(comments) FROM moment_moment"
            
            # 总分享数
            total_shared_sql = "SELECT COUNT(*) FROM moment_moment WHERE is_shared = TRUE"
            
            # 近7天每天的动态数
            daily_sql = """
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as count
                FROM moment_moment
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                GROUP BY DATE(created_at)
                ORDER BY date
            """
            
            # 热门动态（点赞数最多的前5个）
            hot_sql = """
                SELECT 
                    m.id,
                    m.content,
                    m.likes,
                    m.comments,
                    m.created_at,
                    u.name
                FROM moment_moment m
                INNER JOIN core_user u ON m.user_id = u.id
                ORDER BY m.likes DESC
                LIMIT 5
            """
            
            with connection.cursor() as cursor:
                # 获取总动态数
                cursor.execute(total_sql)
                total_moments = cursor.fetchone()[0]
                
                # 获取总点赞数
                cursor.execute(total_likes_sql)
                total_likes = cursor.fetchone()[0] or 0
                
                # 获取总评论数
                cursor.execute(total_comments_sql)
                total_comments = cursor.fetchone()[0] or 0
                
                # 获取总分享数
                cursor.execute(total_shared_sql)
                total_shared = cursor.fetchone()[0]
                
                # 获取近7天动态数
                cursor.execute(daily_sql)
                daily_data = []
                for row in cursor.fetchall():
                    daily_data.append({
                        'date': row[0].strftime('%Y-%m-%d'),
                        'count': row[1]
                    })
                
                # 获取热门动态
                cursor.execute(hot_sql)
                hot_moments = []
                for row in cursor.fetchall():
                    hot_moments.append({
                        'id': row[0],
                        'content': row[1][:100] + '...' if len(row[1]) > 100 else row[1],
                        'likes': row[2],
                        'comments': row[3],
                        'created_at': row[4].strftime('%Y-%m-%d %H:%M:%S'),
                        'name': row[5]
                    })
            
            return Response({
                'total_moments': total_moments,
                'total_likes': total_likes,
                'total_comments': total_comments,
                'total_shared': total_shared,
                'daily_data': daily_data,
                'hot_moments': hot_moments
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommentViewSet(viewsets.ViewSet):
    """评论管理视图集 - 使用SQL操作"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def list(self, request):
        """获取评论列表"""
        try:
            # 获取查询参数
            search = request.query_params.get('search', '')
            user_id = request.query_params.get('user_id', '')
            moment_id = request.query_params.get('moment_id', '')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            # 构建基础SQL查询
            sql = """
                SELECT 
                    c.id,
                    c.content,
                    c.likes,
                    c.created_at,
                    u.username,
                    u.email,
                    m.content as moment_content,
                    m.id as moment_id
                FROM moment_comment c
                INNER JOIN core_user u ON c.user_id = u.id
                INNER JOIN moment_moment m ON c.moment_id = m.id
                WHERE 1=1
            """
            
            params = []
            
            # 添加搜索条件
            if search:
                sql += " AND (c.content LIKE %s OR u.username LIKE %s)"
                search_param = f"%{search}%"
                params.extend([search_param, search_param])
            
            # 添加用户筛选
            if user_id:
                sql += " AND c.user_id = %s"
                params.append(int(user_id))
            
            # 添加动态筛选
            if moment_id:
                sql += " AND c.moment_id = %s"
                params.append(int(moment_id))
            
            # 添加排序
            sql += " ORDER BY c.created_at DESC"
            
            # 获取总数
            count_sql = sql.replace("SELECT c.id, c.content, c.likes, c.created_at, u.username, u.email, m.content as moment_content, m.id as moment_id", "SELECT COUNT(*)")
            with connection.cursor() as cursor:
                cursor.execute(count_sql, params)
                total = cursor.fetchone()[0]
            
            # 添加分页
            offset = (page - 1) * page_size
            sql += " LIMIT %s OFFSET %s"
            params.extend([page_size, offset])
            
            # 执行查询
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                comments = []
                for row in cursor.fetchall():
                    comment = dict(zip(columns, row))
                    comments.append(comment)
            
            return Response({
                'count': total,
                'results': comments,
                'next': None if page * page_size >= total else f'?page={page + 1}',
                'previous': None if page <= 1 else f'?page={page - 1}'
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, pk=None):
        """获取单个评论详情"""
        try:
            sql = """
                SELECT 
                    c.id,
                    c.content,
                    c.likes,
                    c.created_at,
                    u.username,
                    u.email,
                    m.content as moment_content,
                    m.id as moment_id
                FROM moment_comment c
                INNER JOIN core_user u ON c.user_id = u.id
                INNER JOIN moment_moment m ON c.moment_id = m.id
                WHERE c.id = %s
            """
            
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                result = cursor.fetchone()
                
            if result:
                columns = ['id', 'content', 'likes', 'created_at', 'username', 'email', 'moment_content', 'moment_id']
                comment = dict(zip(columns, result))
                return Response(comment)
            else:
                return Response({
                    'error': '评论不存在'
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, pk=None):
        """删除评论"""
        try:
            # 首先删除相关的评论点赞
            delete_comment_likes_sql = "DELETE FROM moment_commentlike WHERE comment_id = %s"
            with connection.cursor() as cursor:
                cursor.execute(delete_comment_likes_sql, [pk])
            
            # 删除评论
            delete_comment_sql = "DELETE FROM moment_comment WHERE id = %s"
            with connection.cursor() as cursor:
                cursor.execute(delete_comment_sql, [pk])
            
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)