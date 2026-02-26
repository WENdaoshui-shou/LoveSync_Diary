from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib.auth import get_user_model
from django.db import connection

User = get_user_model()


class CommunityEventViewSet(viewsets.ViewSet):
    """社区活动管理视图集 - 使用SQL操作"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def list(self, request):
        """获取活动列表"""
        try:
            # 获取查询参数
            search = request.query_params.get('search', '')
            status_filter = request.query_params.get('status', '')
            is_pinned = request.query_params.get('is_pinned', '')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            # 构建基础SQL查询
            sql = """
                SELECT 
                    id,
                    title,
                    description,
                    status,
                    image,
                    start_date,
                    end_date,
                    location,
                    participant_count,
                    prize_info,
                    is_pinned,
                    created_at,
                    updated_at
                FROM community_event
                WHERE 1=1
            """
            
            params = []
            
            # 添加搜索条件
            if search:
                sql += " AND (title LIKE %s OR description LIKE %s OR location LIKE %s)"
                search_param = f"%{search}%"
                params.extend([search_param, search_param, search_param])
            
            # 添加状态筛选
            if status_filter:
                sql += " AND status = %s"
                params.append(status_filter)
            
            # 添加置顶筛选
            if is_pinned in ['true', 'false']:
                sql += " AND is_pinned = %s"
                params.append(is_pinned == 'true')
            
            # 添加排序
            sql += " ORDER BY is_pinned DESC, created_at DESC"
            
            # 获取总数
            count_sql = sql.replace("SELECT id, title, description, status, image, start_date, end_date, location, participant_count, prize_info, is_pinned, created_at, updated_at", "SELECT COUNT(*)")
            with connection.cursor() as cursor:
                cursor.execute(count_sql, params)
                result = cursor.fetchone()
                total = result[0] if result else 0
            
            # 添加分页
            offset = (page - 1) * page_size
            sql += " LIMIT %s OFFSET %s"
            params.extend([page_size, offset])
            
            # 执行查询
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                events = []
                for row in cursor.fetchall():
                    event = dict(zip(columns, row))
                    # 格式化状态显示
                    status_map = {'active': '进行中', 'upcoming': '即将开始', 'ended': '已结束'}
                    event['status_display'] = status_map.get(event['status'], '未知')
                    # 生成完整的图片URL
                    from sys_LoveSync.storage import AliyunOSSStorage
                    storage = AliyunOSSStorage()
                    image = event.get('image')
                    if image:
                        event['image'] = storage.url(image)
                    events.append(event)
            
            return Response({
                'count': total,
                'results': events,
                'next': None if page * page_size >= total else f'?page={page + 1}',
                'previous': None if page <= 1 else f'?page={page - 1}'
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取活动统计数据"""
        try:
            # 总活动数
            total_sql = "SELECT COUNT(*) FROM community_event"
            
            # 进行中的活动数
            active_sql = "SELECT COUNT(*) FROM community_event WHERE status = 'active'"
            
            # 即将开始的活动数
            upcoming_sql = "SELECT COUNT(*) FROM community_event WHERE status = 'upcoming'"
            
            # 已结束的活动数
            ended_sql = "SELECT COUNT(*) FROM community_event WHERE status = 'ended'"
            
            # 总参与人数
            total_participants_sql = "SELECT SUM(participant_count) FROM community_event"
            
            with connection.cursor() as cursor:
                # 获取总活动数
                cursor.execute(total_sql)
                total_events = cursor.fetchone()[0] or 0
                
                # 获取进行中的活动数
                cursor.execute(active_sql)
                active_events = cursor.fetchone()[0] or 0
                
                # 获取即将开始的活动数
                cursor.execute(upcoming_sql)
                upcoming_events = cursor.fetchone()[0] or 0
                
                # 获取已结束的活动数
                cursor.execute(ended_sql)
                ended_events = cursor.fetchone()[0] or 0
                
                # 获取总参与人数
                cursor.execute(total_participants_sql)
                total_participants = cursor.fetchone()[0] or 0
            
            return Response({
                'total_events': total_events,
                'activeEvents': active_events,
                'upcomingEvents': upcoming_events,
                'ended_events': ended_events,
                'totalParticipants': total_participants
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request):
        """创建活动"""
        try:
            data = request.data
            
            # 处理日期时间格式，将ISO格式转换为MySQL接受的格式
            def format_datetime(datetime_str):
                if not datetime_str:
                    return None
                try:
                    import datetime
                    # 解析ISO格式的日期时间字符串
                    dt = datetime.datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                    # 转换为MySQL接受的格式
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    return None
            
            # 插入新活动
            sql = """
                INSERT INTO community_event (
                    title, description, status, image, 
                    start_date, end_date, location, participant_count, 
                    prize_info, is_pinned, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """
            
            params = [
                data.get('title', ''),
                data.get('description', ''),
                data.get('status', 'upcoming'),
                data.get('image', ''),
                format_datetime(data.get('start_date')),
                format_datetime(data.get('end_date')),
                data.get('location', ''),
                0,  # participant_count
                data.get('prize_info', ''),
                data.get('is_pinned', False)
            ]
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                event_id = cursor.lastrowid
            
            # 返回新创建的活动
            return self.retrieve(request, event_id)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, pk=None):
        """获取单个活动详情"""
        try:
            sql = """
                SELECT 
                    id,
                    title,
                    description,
                    status,
                    image,
                    start_date,
                    end_date,
                    location,
                    participant_count,
                    prize_info,
                    is_pinned,
                    created_at,
                    updated_at
                FROM community_event
                WHERE id = %s
            """
            
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                result = cursor.fetchone()
                
            if result:
                columns = ['id', 'title', 'description', 'status', 'image', 'start_date', 'end_date', 
                          'location', 'participant_count', 'prize_info', 'is_pinned', 'created_at', 'updated_at']
                event = dict(zip(columns, result))
                # 格式化状态显示
                status_map = {'active': '进行中', 'upcoming': '即将开始', 'ended': '已结束'}
                event['status_display'] = status_map.get(event['status'], '未知')
                # 生成完整的图片URL
                from sys_LoveSync.storage import AliyunOSSStorage
                storage = AliyunOSSStorage()
                image = event.get('image')
                if image:
                    event['image'] = storage.url(image)
                return Response(event)
            else:
                return Response({
                    'error': '活动不存在'
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, pk=None):
        """删除活动"""
        try:
            # 执行删除操作
            sql = "DELETE FROM community_event WHERE id = %s"
            
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                affected_rows = cursor.rowcount
            
            if affected_rows > 0:
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({
                    'error': '活动不存在'
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """切换活动状态"""
        try:
            # 先获取当前状态
            sql = "SELECT status FROM community_event WHERE id = %s"
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                result = cursor.fetchone()
                
            if not result:
                return Response({
                    'error': '活动不存在'
                }, status=status.HTTP_404_NOT_FOUND)
            
            current_status = result[0]
            
            # 状态转换逻辑
            status_transitions = {
                'active': 'ended',      # 进行中 -> 已结束
                'upcoming': 'active',   # 即将开始 -> 进行中
                'ended': 'upcoming'     # 已结束 -> 即将开始
            }
            
            new_status = status_transitions.get(current_status, 'upcoming')
            
            # 更新状态
            update_sql = "UPDATE community_event SET status = %s, updated_at = NOW() WHERE id = %s"
            with connection.cursor() as cursor:
                cursor.execute(update_sql, [new_status, pk])
            
            # 返回更新后的活动
            return self.retrieve(request, pk)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def toggle_pin(self, request, pk=None):
        """切换活动置顶状态"""
        try:
            # 先获取当前置顶状态
            sql = "SELECT is_pinned FROM community_event WHERE id = %s"
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                result = cursor.fetchone()
                
            if not result:
                return Response({
                    'error': '活动不存在'
                }, status=status.HTTP_404_NOT_FOUND)
            
            current_pinned = result[0]
            new_pinned = not current_pinned
            
            # 更新置顶状态
            update_sql = "UPDATE community_event SET is_pinned = %s, updated_at = NOW() WHERE id = %s"
            with connection.cursor() as cursor:
                cursor.execute(update_sql, [new_pinned, pk])
            
            # 返回更新后的活动
            return self.retrieve(request, pk)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TopicViewSet(viewsets.ViewSet):
    """话题管理视图集 - 使用SQL操作"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def list(self, request):
        """获取话题列表"""
        try:
            # 获取查询参数
            search = request.query_params.get('search', '')
            status_filter = request.query_params.get('status', '')
            heat_level = request.query_params.get('heat_level', '')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            # 构建基础SQL查询 - 基于标签表和动态统计
            sql = """
                SELECT 
                    t.id,
                    t.name as title,
                    t.name as description,
                    COUNT(m.id) as discussion_count,
                    0 as view_count,
                    0 as like_count,
                    CASE 
                        WHEN COUNT(m.id) >= 50 THEN 'hot'
                        WHEN COUNT(m.id) >= 20 THEN 'active'
                        ELSE 'normal'
                    END as status,
                    CASE 
                        WHEN COUNT(m.id) >= 50 THEN 3
                        WHEN COUNT(m.id) >= 20 THEN 2
                        ELSE 1
                    END as heat_level,
                    t.created_at,
                    t.created_at as updated_at
                FROM moment_tag t
                LEFT JOIN moment_moment_tags mt ON t.id = mt.tag_id
                LEFT JOIN moment_moment m ON mt.moment_id = m.id
                WHERE 1=1
            """
            
            params = []
            
            # 添加搜索条件
            if search:
                sql += " AND t.name LIKE %s"
                params.append(f"%{search}%")
            
            # 添加状态筛选
            if status_filter:
                if status_filter == 'active':
                    sql += " AND (SELECT COUNT(*) FROM moment_moment_tags mt2 WHERE mt2.tag_id = t.id) >= 20 AND (SELECT COUNT(*) FROM moment_moment_tags mt2 WHERE mt2.tag_id = t.id) < 50"
                elif status_filter == 'hot':
                    sql += " AND (SELECT COUNT(*) FROM moment_moment_tags mt2 WHERE mt2.tag_id = t.id) >= 50"
                elif status_filter == 'normal':
                    sql += " AND (SELECT COUNT(*) FROM moment_moment_tags mt2 WHERE mt2.tag_id = t.id) < 20"
            
            # 添加热度筛选
            if heat_level:
                if heat_level == '3':
                    sql += " HAVING COUNT(m.id) >= 50"
                elif heat_level == '2':
                    sql += " HAVING COUNT(m.id) >= 20 AND COUNT(m.id) < 50"
                elif heat_level == '1':
                    sql += " HAVING COUNT(m.id) < 20"
            
            # 添加分组和排序
            sql += " GROUP BY t.id, t.name, t.created_at"
            sql += " ORDER BY COUNT(m.id) DESC, t.created_at DESC"
            
            # 获取总数
            count_sql = """
                SELECT COUNT(DISTINCT t.id)
                FROM moment_tag t
                LEFT JOIN moment_moment_tags mt ON t.id = mt.tag_id
                LEFT JOIN moment_moment m ON mt.moment_id = m.id
                WHERE 1=1
            """
            count_params = params.copy()
            
            if search:
                count_sql += " AND t.name LIKE %s"
                count_params.append(f"%{search}%")
            
            with connection.cursor() as cursor:
                cursor.execute(count_sql, count_params)
                total = cursor.fetchone()[0]
            
            # 添加分页
            offset = (page - 1) * page_size
            sql += " LIMIT %s OFFSET %s"
            params.extend([page_size, offset])
            
            # 执行查询
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                topics = []
                for row in cursor.fetchall():
                    topic = dict(zip(columns, row))
                    # 添加图标
                    topic['icon'] = self._get_topic_icon(topic['title'])
                    topics.append(topic)
            
            return Response({
                'count': total,
                'results': topics,
                'next': None if page * page_size >= total else f'?page={page + 1}',
                'previous': None if page <= 1 else f'?page={page - 1}'
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request):
        """创建话题"""
        try:
            data = request.data
            
            # 插入新标签作为话题
            sql = """
                INSERT INTO moment_tag (name, created_at)
                VALUES (%s, NOW())
            """
            
            params = [data.get('title', '')]
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                topic_id = cursor.lastrowid
            
            # 返回新创建的话题
            return self._get_topic_by_id(topic_id)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, pk=None):
        """获取单个话题详情"""
        return self._get_topic_by_id(pk)
    
    def update(self, request, pk=None):
        """更新话题"""
        try:
            data = request.data
            
            sql = """
                UPDATE moment_tag SET
                    name = %s
                WHERE id = %s
            """
            
            params = [data.get('title', ''), pk]
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
            
            # 返回更新后的话题
            return self._get_topic_by_id(pk)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, pk=None):
        """删除话题"""
        try:
            # 首先删除关联的动态标签关系
            delete_relations_sql = "DELETE FROM moment_moment_tags WHERE tag_id = %s"
            with connection.cursor() as cursor:
                cursor.execute(delete_relations_sql, [pk])
            
            # 然后删除标签（话题）
            delete_topic_sql = "DELETE FROM moment_tag WHERE id = %s"
            with connection.cursor() as cursor:
                cursor.execute(delete_topic_sql, [pk])
            
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """切换话题状态（开启/关闭）"""
        try:
            # 获取当前话题的讨论数
            current_sql = """
                SELECT COUNT(m.id) as discussion_count
                FROM moment_tag t
                LEFT JOIN moment_moment_tags mt ON t.id = mt.tag_id
                LEFT JOIN moment_moment m ON mt.moment_id = m.id
                WHERE t.id = %s
                GROUP BY t.id
            """
            
            with connection.cursor() as cursor:
                cursor.execute(current_sql, [pk])
                result = cursor.fetchone()
                discussion_count = result[0] if result else 0
            
            # 这里只是返回当前状态，实际的状态由讨论数决定
            return Response({
                'id': pk,
                'discussion_count': discussion_count,
                'status': 'hot' if discussion_count >= 50 else 'active' if discussion_count >= 20 else 'normal',
                'message': '话题状态已更新'
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取话题统计数据"""
        try:
            # 总话题数（标签数）
            total_sql = "SELECT COUNT(*) FROM moment_tag"
            
            # 活跃话题数（讨论数>=20）
            active_sql = """
                SELECT COUNT(DISTINCT t.id)
                FROM moment_tag t
                LEFT JOIN moment_moment_tags mt ON t.id = mt.tag_id
                LEFT JOIN moment_moment m ON mt.moment_id = m.id
                GROUP BY t.id
                HAVING COUNT(m.id) >= 20
            """
            
            # 热门话题数（讨论数>=50）
            hot_sql = """
                SELECT COUNT(DISTINCT t.id)
                FROM moment_tag t
                LEFT JOIN moment_moment_tags mt ON t.id = mt.tag_id
                LEFT JOIN moment_moment m ON mt.moment_id = m.id
                GROUP BY t.id
                HAVING COUNT(m.id) >= 50
            """
            
            # 总讨论数（动态总数）
            total_discussions_sql = "SELECT COUNT(*) FROM moment_moment"
            
            with connection.cursor() as cursor:
                # 获取总话题数
                cursor.execute(total_sql)
                total_topics = cursor.fetchone()[0]
                
                # 获取活跃话题数
                cursor.execute(active_sql)
                active_topics = len(cursor.fetchall())
                
                # 获取热门话题数
                cursor.execute(hot_sql)
                hot_topics = len(cursor.fetchall())
                
                # 获取总讨论数
                cursor.execute(total_discussions_sql)
                total_discussions = cursor.fetchone()[0]
            
            return Response({
                'total_topics': total_topics,
                'active_topics': active_topics,
                'hot_topics': hot_topics,
                'total_discussions': total_discussions
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_topic_by_id(self, topic_id):
        """根据ID获取话题详情"""
        try:
            sql = """
                SELECT 
                    t.id,
                    t.name as title,
                    t.name as description,
                    COUNT(m.id) as discussion_count,
                    0 as view_count,
                    0 as like_count,
                    CASE 
                        WHEN COUNT(m.id) >= 50 THEN 'hot'
                        WHEN COUNT(m.id) >= 20 THEN 'active'
                        ELSE 'normal'
                    END as status,
                    CASE 
                        WHEN COUNT(m.id) >= 50 THEN 3
                        WHEN COUNT(m.id) >= 20 THEN 2
                        ELSE 1
                    END as heat_level,
                    t.created_at,
                    t.created_at as updated_at
                FROM moment_tag t
                LEFT JOIN moment_moment_tags mt ON t.id = mt.tag_id
                LEFT JOIN moment_moment m ON mt.moment_id = m.id
                WHERE t.id = %s
                GROUP BY t.id, t.name, t.created_at
            """
            
            with connection.cursor() as cursor:
                cursor.execute(sql, [topic_id])
                result = cursor.fetchone()
                
            if result:
                columns = ['id', 'title', 'description', 'discussion_count', 'view_count', 'like_count', 
                          'status', 'heat_level', 'created_at', 'updated_at']
                topic = dict(zip(columns, result))
                topic['icon'] = self._get_topic_icon(topic['title'])
                return Response(topic)
            else:
                return Response({
                    'error': '话题不存在'
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_topic_icon(self, title):
        """根据话题标题获取合适的图标"""
        title_lower = title.lower()
        icon_map = {
            '情人节': 'el-icon-heart',
            '摄影': 'el-icon-camera',
            '美食': 'el-icon-food',
            '旅行': 'el-icon-location',
            '运动': 'el-icon-basketball',
            '音乐': 'el-icon-headset',
            '电影': 'el-icon-video-play',
            '读书': 'el-icon-reading',
            '学习': 'el-icon-notebook-1',
            '工作': 'el-icon-briefcase',
            '生活': 'el-icon-house',
            '宠物': 'el-icon-chicken',
            '时尚': 'el-icon-shopping-bag-1',
            '健康': 'el-icon-first-aid-kit',
            '科技': 'el-icon-monitor',
            '游戏': 'el-icon-coordinate'
        }
        
        for keyword, icon in icon_map.items():
            if keyword in title_lower:
                return icon
        
        return 'el-icon-chat-dot-round'  # 默认图标


class ReportViewSet(viewsets.ViewSet):
    """举报管理视图集 - 使用SQL操作"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_permissions(self):
        """根据动作设置不同的权限"""
        if self.action == 'create_public':
            return [IsAuthenticated()]  # 普通用户也可以创建举报
        return [IsAuthenticated(), IsAdminUser()]  # 其他操作需要管理员权限
    
    def list(self, request):
        """获取举报列表"""
        try:
            # 获取查询参数
            search = request.query_params.get('search', '')
            status_filter = request.query_params.get('status', '')
            report_type = request.query_params.get('report_type', '')
            priority = request.query_params.get('priority', '')
            is_urgent = request.query_params.get('is_urgent', '')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            # 构建基础SQL查询
            sql = """
                SELECT 
                    r.id,
                    r.title,
                    r.description,
                    r.report_type,
                    r.status,
                    r.priority,
                    r.is_urgent,
                    r.created_at,
                    r.reviewed_at,
                    r.resolved_at,
                    r.action_taken,
                    r.content_type,
                    r.content_id,
                    r.content_title,
                    reporter.username as reporter_username,
                    reporter.name as reporter_name,
                    reporter.id as reporter_id,
                    reporter_profile.userAvatar as reporter_avatar,
                    reported_user.name as reported_user_name,
                    reported_user.username as reported_user_username,
                    reported_user.id as reported_user_id,
                    reported_user_profile.userAvatar as reported_user_avatar
                FROM community_report r
                INNER JOIN core_user reporter ON r.reporter_id = reporter.id
                LEFT JOIN core_profile reporter_profile ON reporter.id = reporter_profile.user_id
                INNER JOIN core_user reported_user ON r.reported_user_id = reported_user.id
                LEFT JOIN core_profile reported_user_profile ON reported_user.id = reported_user_profile.user_id
                WHERE 1=1
            """

            
            params = []
            
            # 添加搜索条件
            if search:
                sql += " AND (r.title LIKE %s OR r.description LIKE %s OR reporter.username LIKE %s OR reported_user.username LIKE %s)"
                search_param = f"%{search}%"
                params.extend([search_param, search_param, search_param, search_param])
            
            # 添加状态筛选
            if status_filter:
                sql += " AND r.status = %s"
                params.append(status_filter)
            
            # 添加类型筛选
            if report_type:
                sql += " AND r.report_type = %s"
                params.append(report_type)
            
            # 添加优先级筛选
            if priority:
                sql += " AND r.priority = %s"
                params.append(int(priority))
            
            # 添加紧急筛选
            if is_urgent in ['true', 'false']:
                sql += " AND r.is_urgent = %s"
                params.append(is_urgent == 'true')
            
            # 添加排序
            sql += " ORDER BY r.priority DESC, r.created_at DESC"
            
            # 获取总数
            count_sql = "SELECT COUNT(*) FROM community_report r INNER JOIN core_user reporter ON r.reporter_id = reporter.id LEFT JOIN core_profile reporter_profile ON reporter.id = reporter_profile.user_id INNER JOIN core_user reported_user ON r.reported_user_id = reported_user.id LEFT JOIN core_profile reported_user_profile ON reported_user.id = reported_user_profile.user_id WHERE 1=1"
            
            # 添加搜索条件
            if search:
                count_sql += " AND (r.title LIKE %s OR r.description LIKE %s OR reporter.username LIKE %s OR reported_user.username LIKE %s)"
            
            # 添加状态筛选
            if status_filter:
                count_sql += " AND r.status = %s"
            
            # 添加类型筛选
            if report_type:
                count_sql += " AND r.report_type = %s"
            
            # 添加优先级筛选
            if priority:
                count_sql += " AND r.priority = %s"
            
            # 添加紧急筛选
            if is_urgent in ['true', 'false']:
                count_sql += " AND r.is_urgent = %s"
            
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
                reports = []
                for row in cursor.fetchall():
                    report = dict(zip(columns, row))
                    # 格式化状态显示
                    status_map = {'pending': '待处理', 'reviewing': '审核中', 'resolved': '已处理', 'dismissed': '已驳回'}
                    report['status_display'] = status_map.get(report['status'], '未知')
                    report['priority_display'] = {1: '低', 2: '中', 3: '高'}.get(report['priority'], '未知')
                    reports.append(report)
            
            return Response({
                'count': total,
                'results': reports,
                'next': None if page * page_size >= total else f'?page={page + 1}',
                'previous': None if page <= 1 else f'?page={page - 1}'
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request):
        """创建举报"""
        try:
            data = request.data
            
            sql = """
                INSERT INTO community_report (
                    reporter_id, reported_user_id, report_type, title, description,
                    evidence, status, priority, is_urgent, content_type, content_id,
                    content_title, created_at, reviewed_at, resolved_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NULL, NULL)
            """
            
            params = [
                data.get('reporter_id', request.user.id),
                data.get('reported_user_id'),
                data.get('report_type', 'other'),
                data.get('title', ''),
                data.get('description', ''),
                data.get('evidence', ''),
                data.get('status', 'pending'),
                data.get('priority', 1),
                data.get('is_urgent', False),
                data.get('content_type', None),
                data.get('content_id', None),
                data.get('content_title', '')
            ]
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                report_id = cursor.lastrowid
            
            # 返回新创建的举报
            return self._get_report_by_id(report_id)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, pk=None):
        """获取单个举报详情"""
        return self._get_report_by_id(pk)
    
    def update(self, request, pk=None):
        """更新举报"""
        try:
            data = request.data
            
            sql = """
                UPDATE community_report SET
                    report_type = %s,
                    title = %s,
                    description = %s,
                    evidence = %s,
                    status = %s,
                    priority = %s,
                    is_urgent = %s,
                    content_type = %s,
                    content_id = %s,
                    content_title = %s,
                    reviewed_by_id = %s,
                    reviewed_at = %s,
                    resolved_at = %s,
                    action_taken = %s,
                    review_notes = %s
                WHERE id = %s
            """
            
            params = [
                data.get('report_type'),
                data.get('title', ''),
                data.get('description', ''),
                data.get('evidence', ''),
                data.get('status', 'pending'),
                data.get('priority', 1),
                data.get('is_urgent', False),
                data.get('content_type', None),
                data.get('content_id', None),
                data.get('content_title', ''),
                data.get('reviewed_by_id', request.user.id),
                data.get('reviewed_at', None),
                data.get('resolved_at', None),
                data.get('action_taken', ''),
                data.get('review_notes', ''),
                pk
            ]
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
            
            # 返回更新后的举报
            return self._get_report_by_id(pk)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, pk=None):
        """删除举报"""
        try:
            sql = "DELETE FROM community_report WHERE id = %s"
            
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
            
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def start_review(self, request, pk=None):
        """开始审核举报"""
        try:
            # 先获取当前状态
            sql = "SELECT status FROM community_report WHERE id = %s"
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                result = cursor.fetchone()
                
            if not result:
                return Response({
                    'error': '举报不存在'
                }, status=status.HTTP_404_NOT_FOUND)
            
            current_status = result[0]
            
            if current_status != 'pending':
                return Response({
                    'error': '该举报状态不允许开始审核'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 更新状态
            update_sql = """
                UPDATE community_report SET 
                    status = 'reviewing',
                    reviewed_by_id = %s,
                    reviewed_at = NOW()
                WHERE id = %s
            """
            with connection.cursor() as cursor:
                cursor.execute(update_sql, [request.user.id, pk])
            
            # 返回更新后的举报
            return self._get_report_by_id(pk)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """处理举报"""
        try:
            action_taken = request.data.get('action_taken', '')
            
            # 先获取当前状态
            sql = "SELECT status FROM community_report WHERE id = %s"
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                result = cursor.fetchone()
                
            if not result:
                return Response({
                    'error': '举报不存在'
                }, status=status.HTTP_404_NOT_FOUND)
            
            current_status = result[0]
            
            if current_status not in ['pending', 'reviewing']:
                return Response({
                    'error': '该举报状态不允许处理'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 更新状态
            update_sql = """
                UPDATE community_report SET 
                    status = 'resolved',
                    action_taken = %s,
                    resolved_at = NOW()
                WHERE id = %s
            """
            with connection.cursor() as cursor:
                cursor.execute(update_sql, [action_taken, pk])
            
            # 返回更新后的举报
            return self._get_report_by_id(pk)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """驳回举报"""
        try:
            review_notes = request.data.get('review_notes', '')
            
            # 先获取当前状态
            sql = "SELECT status FROM community_report WHERE id = %s"
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                result = cursor.fetchone()
                
            if not result:
                return Response({
                    'error': '举报不存在'
                }, status=status.HTTP_404_NOT_FOUND)
            
            current_status = result[0]
            
            if current_status not in ['pending', 'reviewing']:
                return Response({
                    'error': '该举报状态不允许驳回'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 更新状态
            update_sql = """
                UPDATE community_report SET 
                    status = 'dismissed',
                    review_notes = %s,
                    resolved_at = NOW()
                WHERE id = %s
            """
            with connection.cursor() as cursor:
                cursor.execute(update_sql, [review_notes, pk])
            
            # 返回更新后的举报
            return self._get_report_by_id(pk)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], url_path='create_public')
    def create_public(self, request):
        """公开API：创建举报（普通用户可用）"""
        try:
            # 设置举报人和被举报人
            data = request.data.copy()
            reporter_id = request.user.id
            reported_user_id = data.get('reported_user')
            
            if not reported_user_id:
                return Response({
                    'error': '请提供被举报人信息'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 验证被举报人是否存在
            check_sql = "SELECT id FROM core_user WHERE id = %s"
            with connection.cursor() as cursor:
                cursor.execute(check_sql, [reported_user_id])
                if not cursor.fetchone():
                    return Response({
                        'error': '被举报人不存在'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
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
            
            # 返回新创建的举报
            return self._get_report_by_id(report_id)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        """获取举报统计数据"""
        try:
            # 获取总举报数、待处理举报数、已处理举报数和处理率
            sql = """
                SELECT 
                    COUNT(*) as total_reports,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_reports,
                    SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) as resolved_reports,
                    ROUND(IFNULL((SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) / COUNT(*)) * 100, 0), 2) as resolution_rate
                FROM community_report
            """
            
            # 获取今日新增举报数
            today_sql = """
                SELECT COUNT(*) as today_reports
                FROM community_report
                WHERE DATE(created_at) = CURDATE()
            """
            
            with connection.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchone()
                
                cursor.execute(today_sql)
                today_result = cursor.fetchone()
            
            if result:
                pending_reports = result[1] or 0
                resolution_rate = result[3] or 0
                statistics = {
                    'totalReports': result[0] or 0,
                    'pendingReports': pending_reports,
                    'resolvedReports': result[2] or 0,
                    'todayReports': today_result[0] or 0,
                    'reportResolutionRate': f'{resolution_rate}%'
                }
            else:
                statistics = {
                    'totalReports': 0,
                    'pendingReports': 0,
                    'resolvedReports': 0,
                    'todayReports': 0,
                    'reportResolutionRate': '0%'
                }
            
            return Response(statistics)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_report_by_id(self, report_id):
        """根据ID获取举报详情"""
        try:
            sql = """
                SELECT 
                    r.id,
                    r.title,
                    r.description,
                    r.report_type,
                    r.status,
                    r.priority,
                    r.is_urgent,
                    r.created_at,
                    r.reviewed_at,
                    r.resolved_at,
                    r.action_taken,
                    r.content_type,
                    r.content_id,
                    r.content_title,
                    r.review_notes,
                    reporter.username as reporter_name,
                    reporter.id as reporter_id,
                    reporter_profile.userAvatar as reporter_avatar,
                    reported_user.username as reported_user_name,
                    reported_user.id as reported_user_id,
                    reported_user_profile.userAvatar as reported_user_avatar
                FROM community_report r
                INNER JOIN core_user reporter ON r.reporter_id = reporter.id
                LEFT JOIN core_profile reporter_profile ON reporter.id = reporter_profile.user_id
                INNER JOIN core_user reported_user ON r.reported_user_id = reported_user.id
                LEFT JOIN core_profile reported_user_profile ON reported_user.id = reported_user_profile.user_id
                WHERE r.id = %s
            """

            
            with connection.cursor() as cursor:
                cursor.execute(sql, [report_id])
                result = cursor.fetchone()
                
            if result:
                columns = ['id', 'title', 'description', 'report_type', 'status', 'priority', 'is_urgent',
                          'created_at', 'reviewed_at', 'resolved_at', 'action_taken', 'content_type',
                          'content_id', 'content_title', 'review_notes', 'reporter_name', 'reporter_id',
                          'reporter_avatar', 'reported_user_name', 'reported_user_id', 'reported_user_avatar']
                report = dict(zip(columns, result))
                # 格式化状态显示
                status_map = {'pending': '待处理', 'reviewing': '审核中', 'resolved': '已处理', 'dismissed': '已驳回'}
                report['status_display'] = status_map.get(report['status'], '未知')
                report['priority_display'] = {1: '低', 2: '中', 3: '高'}.get(report['priority'], '未知')
                return Response(report)
            else:
                return Response({
                    'error': '举报不存在'
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ArticleColumnViewSet(viewsets.ViewSet):
    """文章专栏管理视图集 - 使用SQL操作"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def list(self, request):
        """获取专栏列表"""
        try:
            # 获取查询参数
            search = request.query_params.get('search', '')
            is_active = request.query_params.get('is_active', '')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            # 构建基础SQL查询
            sql = """
                SELECT 
                    id,
                    name,
                    slug,
                    description,
                    cover_image,
                    category,
                    subscriber_count,
                    view_count,
                    is_active,
                    updated_at
                FROM articles_officialcolumn
                WHERE 1=1
            """
            
            params = []
            
            # 添加搜索条件
            if search:
                sql += " AND (name LIKE %s OR description LIKE %s)"
                search_param = f"%{search}%"
                params.extend([search_param, search_param])
            
            # 添加状态筛选
            if is_active in ['true', 'false']:
                sql += " AND is_active = %s"
                params.append(is_active == 'true')
            
            # 添加排序
            sql += " ORDER BY updated_at DESC"
            
            # 获取总数
            count_sql = sql.replace("SELECT \n                    id,\n                    name,\n                    slug,\n                    description,\n                    cover_image,\n                    category,\n                    subscriber_count,\n                    view_count,\n                    is_active,\n                    updated_at", "SELECT COUNT(*)")
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
                columns_list = []
                for row in cursor.fetchall():
                    column = dict(zip(columns, row))
                    # 添加分类显示
                    category_map = {
                        'love_growth': '恋爱成长手册',
                        'diary_inspiration': '日记灵感库',
                        'festival_special': '节日特辑',
                        'platform_activity': '平台活动通知',
                        'other': '其他'
                    }
                    column['category_display'] = category_map.get(column['category'], '其他')
                    column['status_display'] = '启用' if column['is_active'] else '禁用'
                    columns_list.append(column)
            
            return Response({
                'count': total,
                'results': columns_list,
                'next': None if page * page_size >= total else f'?page={page + 1}',
                'previous': None if page <= 1 else f'?page={page - 1}'
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, pk=None):
        """获取单个专栏详情"""
        try:
            sql = """
                SELECT 
                    id,
                    name,
                    slug,
                    description,
                    cover_image,
                    category,
                    subscriber_count,
                    view_count,
                    is_active,
                    updated_at
                FROM articles_officialcolumn
                WHERE id = %s
            """
            
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                result = cursor.fetchone()
                
            if result:
                columns = ['id', 'name', 'slug', 'description', 'cover_image', 'category', 
                          'subscriber_count', 'view_count', 'is_active', 'updated_at']
                column = dict(zip(columns, result))
                # 添加分类显示
                category_map = {
                    'love_growth': '恋爱成长手册',
                    'diary_inspiration': '日记灵感库',
                    'festival_special': '节日特辑',
                    'platform_activity': '平台活动通知',
                    'other': '其他'
                }
                column['category_display'] = category_map.get(column['category'], '其他')
                column['status_display'] = '启用' if column['is_active'] else '禁用'
                return Response(column)
            else:
                return Response({
                    'error': '专栏不存在'
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request):
        """创建专栏"""
        try:
            data = request.data
            
            sql = """
                INSERT INTO articles_officialcolumn (
                    name, slug, description, cover_image, category,
                    subscriber_count, view_count, is_active, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            
            params = [
                data.get('name', ''),
                data.get('slug', ''),
                data.get('description', ''),
                data.get('cover_image', None),
                data.get('category', 'other'),
                0,  # subscriber_count
                0,  # view_count
                data.get('is_active', True)
            ]
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                column_id = cursor.lastrowid
            
            # 返回新创建的专栏
            return self.retrieve(request, column_id)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, pk=None):
        """更新专栏"""
        try:
            data = request.data
            
            sql = """
                UPDATE articles_officialcolumn SET
                    name = %s,
                    slug = %s,
                    description = %s,
                    cover_image = %s,
                    category = %s,
                    is_active = %s,
                    updated_at = NOW()
                WHERE id = %s
            """
            
            params = [
                data.get('name', ''),
                data.get('slug', ''),
                data.get('description', ''),
                data.get('cover_image', None),
                data.get('category', 'other'),
                data.get('is_active', True),
                pk
            ]
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
            
            # 返回更新后的专栏
            return self.retrieve(request, pk)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, pk=None):
        """删除专栏"""
        try:
            # 首先删除相关的订阅
            delete_subscriptions_sql = "DELETE FROM articles_columnsubscription WHERE column_id = %s"
            with connection.cursor() as cursor:
                cursor.execute(delete_subscriptions_sql, [pk])
            
            # 然后删除专栏
            delete_column_sql = "DELETE FROM articles_officialcolumn WHERE id = %s"
            with connection.cursor() as cursor:
                cursor.execute(delete_column_sql, [pk])
            
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取专栏统计数据"""
        try:
            # 总专栏数
            total_sql = "SELECT COUNT(*) FROM articles_officialcolumn"
            
            # 启用的专栏数
            active_sql = "SELECT COUNT(*) FROM articles_officialcolumn WHERE is_active = TRUE"
            
            # 总订阅数
            total_subscribers_sql = "SELECT SUM(subscriber_count) FROM articles_officialcolumn"
            
            # 总浏览量
            total_views_sql = "SELECT SUM(view_count) FROM articles_officialcolumn"
            
            with connection.cursor() as cursor:
                # 获取总专栏数
                cursor.execute(total_sql)
                total_columns = cursor.fetchone()[0]
                
                # 获取启用的专栏数
                cursor.execute(active_sql)
                active_columns = cursor.fetchone()[0]
                
                # 获取总订阅数
                cursor.execute(total_subscribers_sql)
                total_subscribers = cursor.fetchone()[0] or 0
                
                # 获取总浏览量
                cursor.execute(total_views_sql)
                total_views = cursor.fetchone()[0] or 0
            
            return Response({
                'total_columns': total_columns,
                'active_columns': active_columns,
                'total_subscribers': total_subscribers,
                'total_views': total_views
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)