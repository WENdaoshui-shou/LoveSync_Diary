from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from django.db import connection
from django.contrib.auth import get_user_model
from django.db.models import Count, Q

User = get_user_model()


class UserViewSet(viewsets.ViewSet):
    """用户管理视图集 - 使用SQL操作"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def list(self, request):
        """获取用户列表"""
        try:
            # 获取查询参数
            search = request.query_params.get('search', '')
            is_active = request.query_params.get('is_active', '')
            is_staff = request.query_params.get('is_staff', '')
            is_superuser = request.query_params.get('is_superuser', '')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            # 构建基础SQL查询
            sql = """
                SELECT 
                    id,
                    username,
                    email,
                    name,
                    is_active,
                    is_staff,
                    is_superuser,
                    date_joined,
                    last_login
                FROM core_user
                WHERE 1=1
            """
            
            params = []
            
            # 添加搜索条件
            if search:
                sql += " AND (username LIKE %s OR email LIKE %s OR name LIKE %s)"
                search_param = f"%{search}%"
                params.extend([search_param, search_param, search_param])
            
            # 添加状态筛选
            if is_active in ['true', 'false']:
                sql += " AND is_active = %s"
                params.append(is_active == 'true')
            
            # 添加管理员筛选
            if is_staff in ['true', 'false']:
                sql += " AND is_staff = %s"
                params.append(is_staff == 'true')
            
            # 添加超级用户筛选
            if is_superuser in ['true', 'false']:
                sql += " AND is_superuser = %s"
                params.append(is_superuser == 'true')
            
            # 添加排序
            sql += " ORDER BY date_joined DESC"
            
            # 获取总数
            count_sql = sql.replace("SELECT \n                    id,\n                    username,\n                    email,\n                    name,\n                    is_active,\n                    is_staff,\n                    is_superuser,\n                    date_joined,\n                    last_login","SELECT COUNT(*)")
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
                users = []
                for row in cursor.fetchall():
                    user = dict(zip(columns, row))
                    users.append(user)
            
            return Response({
                'count': total,
                'results': users,
                'next': None if page * page_size >= total else f'?page={page + 1}',
                'previous': None if page <= 1 else f'?page={page - 1}'
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, pk=None):
        """获取单个用户详情"""
        try:
            sql = """
                SELECT 
                    id,
                    username,
                    email,
                    name,
                    avatar,
                    is_active,
                    is_staff,
                    is_superuser,
                    date_joined,
                    last_login,
                    phone,
                    gender,
                    birthday,
                    location,
                    bio,
                    couple_id,
                    created_at,
                    updated_at
                FROM core_user
                WHERE id = %s
            """
            
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                result = cursor.fetchone()
                
            if result:
                columns = ['id', 'username', 'email', 'name', 'avatar', 'is_active', 'is_staff', 'is_superuser', 
                          'date_joined', 'last_login', 'phone', 'gender', 'birthday', 'location', 'bio', 'couple_id', 'created_at', 'updated_at']
                user = dict(zip(columns, result))
                return Response(user)
            else:
                return Response({
                    'error': '用户不存在'
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, pk=None):
        """更新用户信息"""
        try:
            data = request.data
            
            sql = """
                UPDATE core_user SET
                    email = %s,
                    name = %s,
                    phone = %s,
                    gender = %s,
                    birthday = %s,
                    location = %s,
                    bio = %s
                WHERE id = %s
            """
            
            params = [
                data.get('email', ''),
                data.get('name', ''),
                data.get('phone', ''),
                data.get('gender', ''),
                data.get('birthday', None),
                data.get('location', ''),
                data.get('bio', ''),
                pk
            ]
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
            
            # 返回更新后的用户
            return self._get_user_by_id(pk)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, pk=None):
        """删除用户"""
        try:
            # 先删除关联的记录
            # 1. 删除用户成就记录
            achievement_sql = "DELETE FROM user_userachievement WHERE user_id = %s"
            with connection.cursor() as cursor:
                cursor.execute(achievement_sql, [pk])
            
            # 2. 删除用户VIP会员记录
            vip_sql = "DELETE FROM vip_vipmember WHERE user_id = %s"
            with connection.cursor() as cursor:
                cursor.execute(vip_sql, [pk])
            
            # 3. 删除用户个人资料记录
            profile_sql = "DELETE FROM core_profile WHERE user_id = %s"
            with connection.cursor() as cursor:
                cursor.execute(profile_sql, [pk])
            
            # 4. 再硬删除用户
            user_sql = "DELETE FROM core_user WHERE id = %s"
            with connection.cursor() as cursor:
                cursor.execute(user_sql, [pk])
            
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """切换用户活跃状态"""
        try:
            # 先获取当前状态
            sql = "SELECT is_active FROM core_user WHERE id = %s"
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                result = cursor.fetchone()
                
            if not result:
                return Response({
                    'error': '用户不存在'
                }, status=status.HTTP_404_NOT_FOUND)
            
            current_active = result[0]
            new_active = 0 if current_active else 1
            
            # 更新状态
            update_sql = "UPDATE core_user SET is_active = %s WHERE id = %s"
            with connection.cursor() as cursor:
                cursor.execute(update_sql, [new_active, pk])
            
            return Response({
                'success': True,
                'is_active': new_active,
                'message': '用户状态已更新'
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def toggle_staff(self, request, pk=None):
        """切换管理员状态"""
        try:
            # 先获取当前状态
            sql = "SELECT is_staff FROM core_user WHERE id = %s"
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                result = cursor.fetchone()
                
            if not result:
                return Response({
                    'error': '用户不存在'
                }, status=status.HTTP_404_NOT_FOUND)
            
            current_staff = result[0]
            new_staff = not current_staff
            
            # 更新状态
            update_sql = "UPDATE core_user SET is_staff = %s WHERE id = %s"
            with connection.cursor() as cursor:
                cursor.execute(update_sql, [new_staff, pk])
            
            return Response({
                'is_staff': new_staff,
                'message': '管理员状态已更新'
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取用户统计信息"""
        try:
            today = timezone.now().date()
            week_ago = today - timezone.timedelta(days=7)
            
            # 统计查询
            sql = """
                SELECT 
                    COUNT(*) as total_users,
                    SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_users,
                    SUM(CASE WHEN is_staff = 1 THEN 1 ELSE 0 END) as staff_users,
                    SUM(CASE WHEN is_superuser = 1 THEN 1 ELSE 0 END) as superusers,
                    SUM(CASE WHEN DATE(date_joined) = %s THEN 1 ELSE 0 END) as today_users,
                    SUM(CASE WHEN DATE(date_joined) >= %s THEN 1 ELSE 0 END) as week_users
                FROM core_user
            """
            
            with connection.cursor() as cursor:
                cursor.execute(sql, [today, week_ago])
                result = cursor.fetchone()
                
            if result:
                return Response({
                    'total_users': result[0] or 0,
                    'active_users': result[1] or 0,
                    'staff_users': result[2] or 0,
                    'superusers': result[3] or 0,
                    'today_users': result[4] or 0,
                    'week_users': result[5] or 0
                })
            else:
                return Response({
                    'total_users': 0,
                    'active_users': 0,
                    'staff_users': 0,
                    'superusers': 0,
                    'today_users': 0,
                    'week_users': 0
                })
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_user_by_id(self, user_id):
        """根据ID获取用户详情"""
        try:
            sql = """
                SELECT 
                    id,
                    username,
                    email,
                    name,
                    avatar,
                    is_active,
                    is_staff,
                    is_superuser,
                    date_joined,
                    last_login,
                    phone,
                    gender,
                    birthday,
                    location,
                    bio,
                    couple_id,
                    created_at,
                    updated_at
                FROM core_user
                WHERE id = %s
            """
            
            with connection.cursor() as cursor:
                cursor.execute(sql, [user_id])
                result = cursor.fetchone()
                
            if result:
                columns = ['id', 'username', 'email', 'name', 'avatar', 'is_active', 'is_staff', 'is_superuser', 
                          'date_joined', 'last_login', 'phone', 'gender', 'birthday', 'location', 'bio', 'couple_id', 'created_at', 'updated_at']
                user = dict(zip(columns, result))
                return Response(user)
            else:
                return Response({
                    'error': '用户不存在'
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def system_status(self, request):
        """获取系统状态数据"""
        try:
            # 在线用户（最近1小时内活跃的用户）
            online_users_sql = "SELECT COUNT(*) FROM core_user WHERE last_login >= DATE_SUB(NOW(), INTERVAL 1 HOUR)"
            
            # 今日访问（这里假设使用用户登录次数作为访问量的近似）
            today_visits_sql = "SELECT COUNT(*) FROM core_user WHERE DATE(last_login) = CURDATE()"
            
            with connection.cursor() as cursor:
                # 获取在线用户数
                cursor.execute(online_users_sql)
                online_users = cursor.fetchone()[0] or 0
                
                # 获取今日访问数
                cursor.execute(today_visits_sql)
                today_visits = cursor.fetchone()[0] or 0
            
            # 系统版本（硬编码或从配置中读取）
            system_version = "v1.0.0"
            
            return Response({
                'onlineUsers': online_users,
                'todayVisits': today_visits,
                'systemVersion': system_version
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)