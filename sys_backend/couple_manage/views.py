from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from rest_framework.decorators import action
from datetime import datetime

class RecommendedCouplesViewSet(viewsets.ViewSet):
    """推荐情侣管理视图集 - 使用SQL操作"""
    
    def list(self, request):
        """获取绑定情侣关系的用户列表"""
        try:
            # 获取搜索参数
            search = request.query_params.get('search', '')
            status_param = request.query_params.get('status', '')
            
            # 构建SQL查询
            sql = """
                SELECT 
                    cr.id, 
                    cr.user1_id, 
                    u1.name as user1_name, 
                    cr.user2_id, 
                    u2.name as user2_name, 
                    cr.love_vow, 
                    cr.relationship_start_date, 
                    cr.couple_name, 
                    cr.love_story, 
                    cr.created_at, 
                    cr.updated_at
                FROM couple_couplerelation cr
                LEFT JOIN core_user u1 ON cr.user1_id = u1.id
                LEFT JOIN core_user u2 ON cr.user2_id = u2.id
            """
            
            # 添加搜索条件
            where_clauses = []
            params = []
            
            if search:
                where_clauses.append("(u1.username LIKE %s OR u2.username LIKE %s OR cr.couple_name LIKE %s)")
                params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
            
            if status_param == 'coupled':
                # 已经绑定的情侣关系
                pass  # 所有记录都是已绑定的
            elif status_param == 'single':
                # 这里可以添加获取单身用户的逻辑
                pass
            
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            
            sql += " ORDER BY cr.created_at DESC"
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                couples = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return Response(couples)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, pk=None):
        """获取单个情侣关系详情"""
        try:
            sql = """
                SELECT 
                    cr.id, 
                    cr.user1_id, 
                    u1.name as user1_name, 
                    cr.user2_id, 
                    u2.name as user2_name, 
                    cr.love_vow, 
                    cr.relationship_start_date, 
                    cr.couple_name, 
                    cr.love_story, 
                    cr.theme, 
                    cr.primary_color, 
                    cr.secondary_color, 
                    cr.visibility, 
                    cr.show_couple_dynamics, 
                    cr.show_anniversary, 
                    cr.show_gifts, 
                    cr.notify_partner_messages, 
                    cr.notify_dynamics, 
                    cr.notify_anniversary, 
                    cr.created_at, 
                    cr.updated_at
                FROM couple_couplerelation cr
                LEFT JOIN core_user u1 ON cr.user1_id = u1.id
                LEFT JOIN core_user u2 ON cr.user2_id = u2.id
                WHERE cr.id = %s
            """

            
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                row = cursor.fetchone()
                
                if not row:
                    return Response({'error': '情侣关系不存在'}, status=status.HTTP_404_NOT_FOUND)
                
                columns = [col[0] for col in cursor.description]
                couple = dict(zip(columns, row))
            
            return Response(couple)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request):
        """创建情侣关系"""
        try:
            data = request.data
            
            sql = """
                INSERT INTO couple_couplerelation (
                    user1_id, user2_id, love_vow, relationship_start_date, 
                    couple_name, love_story, theme, primary_color, 
                    secondary_color, visibility, show_couple_dynamics, 
                    show_anniversary, show_gifts, notify_partner_messages, 
                    notify_dynamics, notify_anniversary, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """

            
            params = [
                data.get('user1_id'),
                data.get('user2_id'),
                data.get('love_vow', ''),
                data.get('relationship_start_date'),
                data.get('couple_name', ''),
                data.get('love_story', ''),
                data.get('theme', 'light_love'),
                data.get('primary_color', '#FF6B8B'),
                data.get('secondary_color', '#722ED1'),
                data.get('visibility', 'only_me'),
                data.get('show_couple_dynamics', True),
                data.get('show_anniversary', True),
                data.get('show_gifts', False),
                data.get('notify_partner_messages', True),
                data.get('notify_dynamics', True),
                data.get('notify_anniversary', True)
            ]
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                couple_id = cursor.lastrowid
            
            # 返回新创建的情侣关系
            return self.retrieve(request, couple_id)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, pk=None):
        """更新情侣关系"""
        try:
            data = request.data
            
            sql = """
                UPDATE couple_couplerelation SET
                    user1_id = %s,
                    user2_id = %s,
                    love_vow = %s,
                    relationship_start_date = %s,
                    couple_name = %s,
                    love_story = %s,
                    theme = %s,
                    primary_color = %s,
                    secondary_color = %s,
                    visibility = %s,
                    show_couple_dynamics = %s,
                    show_anniversary = %s,
                    show_gifts = %s,
                    notify_partner_messages = %s,
                    notify_dynamics = %s,
                    notify_anniversary = %s,
                    updated_at = NOW()
                WHERE id = %s
            """

            
            params = [
                data.get('user1_id'),
                data.get('user2_id'),
                data.get('love_vow', ''),
                data.get('relationship_start_date'),
                data.get('couple_name', ''),
                data.get('love_story', ''),
                data.get('theme', 'light_love'),
                data.get('primary_color', '#FF6B8B'),
                data.get('secondary_color', '#722ED1'),
                data.get('visibility', 'only_me'),
                data.get('show_couple_dynamics', True),
                data.get('show_anniversary', True),
                data.get('show_gifts', False),
                data.get('notify_partner_messages', True),
                data.get('notify_dynamics', True),
                data.get('notify_anniversary', True),
                pk
            ]
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                
                if cursor.rowcount == 0:
                    return Response({'error': '情侣关系不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            # 返回更新后的情侣关系
            return self.retrieve(request, pk)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, pk=None):
        """删除情侣关系（解除关系）"""
        try:
            sql = "DELETE FROM couple_couplerelation WHERE id = %s"

            
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                
                if cursor.rowcount == 0:
                    return Response({'error': '情侣关系不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            return Response({'message': '解除关系成功'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取情侣统计数据"""
        try:
            # 总情侣数
            total_couples_sql = "SELECT COUNT(*) FROM couple_couplerelation"
            
            # 总推荐数（这里假设推荐数据存储在某个表中，需要根据实际情况调整）
            total_recommendations_sql = "SELECT COUNT(*) FROM couple_couplerecommendation"
            
            # 总测试参与数
            total_tests_sql = "SELECT COUNT(*) FROM couple_quizrecord"
            
            with connection.cursor() as cursor:
                # 获取总情侣数
                cursor.execute(total_couples_sql)
                total_couples = cursor.fetchone()[0] or 0
                
                # 获取总推荐数
                try:
                    cursor.execute(total_recommendations_sql)
                    total_recommendations = cursor.fetchone()[0] or 0
                except:
                    total_recommendations = 0
                
                # 获取总测试参与数
                try:
                    cursor.execute(total_tests_sql)
                    total_tests = cursor.fetchone()[0] or 0
                except:
                    total_tests = 0
            
            return Response({
                'totalCouples': total_couples,
                'totalRecommendations': total_recommendations,
                'totalTests': total_tests
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PlaceManagementViewSet(viewsets.ViewSet):
    """地点管理视图集 - 使用SQL操作"""
    
    def list(self, request):
        """获取情侣地点列表"""
        try:
            # 获取筛选参数
            search = request.query_params.get('search', '')
            place_type = request.query_params.get('type', '')
            
            # 构建SQL查询
            sql = """
                SELECT 
                    id, name, description, address, 
                    latitude, longitude, place_type, rating, 
                    review_count, price_range, image, created_at, updated_at
                FROM couple_coupleplace
            """

            
            # 添加筛选条件
            where_clauses = []
            params = []
            
            if search:
                where_clauses.append("(name LIKE %s OR description LIKE %s OR address LIKE %s)")
                params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
            
            if place_type:
                where_clauses.append("place_type = %s")
                params.append(place_type)
            
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            
            # 添加排序
            sql += " ORDER BY id DESC"
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                places = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return Response(places)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request):
        """创建情侣地点"""
        try:
            data = request.data
            
            sql = """
                INSERT INTO couple_coupleplace (
                    name, description, address, latitude, 
                    longitude, place_type, rating, review_count, 
                    price_range, image, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """

            
            params = [
                data.get('name'),
                data.get('description'),
                data.get('address'),
                data.get('latitude'),
                data.get('longitude'),
                data.get('place_type'),
                data.get('rating', 0),
                data.get('review_count', 0),
                data.get('price_range'),
                data.get('image', None)
            ]
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                place_id = cursor.lastrowid
            
            # 返回新创建的地点
            return self.retrieve(request, place_id)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, pk=None):
        """获取单个情侣地点详情"""
        try:
            sql = """
                SELECT 
                    id, name, description, address, 
                    latitude, longitude, place_type, rating, 
                    review_count, price_range, image, created_at, updated_at
                FROM couple_coupleplace
                WHERE id = %s
            """

            
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                row = cursor.fetchone()
                
                if not row:
                    return Response({'error': '地点不存在'}, status=status.HTTP_404_NOT_FOUND)
                
                columns = [col[0] for col in cursor.description]
                place = dict(zip(columns, row))
            
            return Response(place)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, pk=None):
        """更新情侣地点"""
        try:
            data = request.data
            
            sql = """
                UPDATE couple_coupleplace SET
                    name = %s,
                    description = %s,
                    address = %s,
                    latitude = %s,
                    longitude = %s,
                    place_type = %s,
                    rating = %s,
                    review_count = %s,
                    price_range = %s,
                    image = %s,
                    updated_at = NOW()
                WHERE id = %s
            """

            
            params = [
                data.get('name'),
                data.get('description'),
                data.get('address'),
                data.get('latitude'),
                data.get('longitude'),
                data.get('place_type'),
                data.get('rating'),
                data.get('review_count'),
                data.get('price_range'),
                data.get('image'),
                pk
            ]
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                
                if cursor.rowcount == 0:
                    return Response({'error': '地点不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            # 返回更新后的地点
            return self.retrieve(request, pk)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, pk=None):
        """删除情侣地点"""
        try:
            sql = "DELETE FROM couple_coupleplace WHERE id = %s"

            
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                
                if cursor.rowcount == 0:
                    return Response({'error': '地点不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            return Response({'message': '地点删除成功'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoveTestManagementViewSet(viewsets.ViewSet):
    """爱情测试管理视图集 - 使用SQL操作"""
    
    def list(self, request):
        """获取爱情测试列表"""
        try:
            # 获取筛选参数
            search = request.query_params.get('search', '')
            category = request.query_params.get('category', '')
            
            # 构建SQL查询
            sql = """
                SELECT 
                    cq.id, 
                    cq.question, 
                    cq.options, 
                    cq.category_id,
                    cq.created_at
                FROM couple_quizquestion cq
            """

            
            # 添加筛选条件
            where_clauses = []
            params = []
            
            if search:
                where_clauses.append("question LIKE %s")
                params.append(f'%{search}%')
            
            if category:
                where_clauses.append("category_id = %s")
                params.append(category)
            
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            
            # 添加排序
            sql += " ORDER BY cq.id DESC"
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                tests = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return Response(tests)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request):
        """创建爱情测试"""
        try:
            data = request.data
            
            sql = """
                INSERT INTO couple_quizquestion (
                    question, options, category_id, created_at
                ) VALUES (%s, %s, %s, NOW())
            """
            
            params = [
                data.get('question'),
                data.get('options'),
                data.get('category_id', 1)  # 提供默认值
            ]
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                test_id = cursor.lastrowid
            
            # 返回新创建的测试
            return self.retrieve(request, test_id)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, pk=None):
        """获取单个爱情测试详情"""
        try:
            sql = """
                SELECT 
                    id, question, options, category_id, created_at
                FROM couple_quizquestion
                WHERE id = %s
            """

            
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                row = cursor.fetchone()
                
                if not row:
                    return Response({'error': '测试不存在'}, status=status.HTTP_404_NOT_FOUND)
                
                columns = [col[0] for col in cursor.description]
                test = dict(zip(columns, row))
            
            return Response(test)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, pk=None):
        """更新爱情测试"""
        try:
            data = request.data
            
            sql = """
                UPDATE couple_quizquestion SET
                    question = %s,
                    options = %s,
                    category_id = %s
                WHERE id = %s
            """
            
            params = [
                data.get('question'),
                data.get('options'),
                data.get('category_id', 1),  # 提供默认值
                pk
            ]
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                
                if cursor.rowcount == 0:
                    return Response({'error': '测试不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            # 返回更新后的测试
            return self.retrieve(request, pk)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, pk=None):
        """删除爱情测试"""
        try:
            sql = "DELETE FROM couple_quizquestion WHERE id = %s"
            
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                
                if cursor.rowcount == 0:
                    return Response({'error': '测试不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            return Response({'message': '测试删除成功'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CoupleGameManagementViewSet(viewsets.ViewSet):
    """情侣游戏管理视图集 - 使用SQL操作"""
    
    def list(self, request):
        """获取情侣游戏列表"""
        try:
            # 获取筛选参数
            search = request.query_params.get('search', '')
            type_param = request.query_params.get('type', '')
            status_param = request.query_params.get('status', '')
            
            # 构建SQL查询
            sql = """
                SELECT 
                    id, 
                    name, 
                    description, 
                    game_type as type, 
                    difficulty, 
                    is_active as status, 
                    created_at, 
                    updated_at
                FROM game_game
            """
            
            # 添加筛选条件
            where_clauses = []
            params = []
            
            if search:
                where_clauses.append("(name LIKE %s OR description LIKE %s)")
                params.extend([f'%{search}%', f'%{search}%'])
            
            if type_param:
                where_clauses.append("game_type = %s")
                params.append(type_param)
            
            if status_param:
                # 将前端的status参数转换为is_active值
                is_active = 1 if status_param == 'active' else 0
                where_clauses.append("is_active = %s")
                params.append(is_active)
            
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            
            # 添加排序
            sql += " ORDER BY created_at DESC"
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                games = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # 转换status字段格式和时间格式
            for game in games:
                game['status'] = 'active' if game['status'] else 'inactive'
                # 转换时间格式为年月日时分
                if game.get('created_at'):
                    if isinstance(game['created_at'], datetime):
                        game['created_at'] = game['created_at'].strftime('%Y-%m-%d %H:%M')
                if game.get('updated_at'):
                    if isinstance(game['updated_at'], datetime):
                        game['updated_at'] = game['updated_at'].strftime('%Y-%m-%d %H:%M')
            
            return Response(games)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request):
        """创建情侣游戏"""
        try:
            data = request.data
            
            # 将前端的status参数转换为is_active值
            is_active = 1 if data.get('status', 'active') == 'active' else 0
            
            sql = """
                INSERT INTO game_game (
                    name, description, game_type, difficulty, is_active, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
            """
            
            params = [
                data.get('name'),
                data.get('description'),
                data.get('type'),
                data.get('difficulty', 'easy'),
                is_active
            ]
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                game_id = cursor.lastrowid
            
            # 返回新创建的游戏
            return self.retrieve(request, game_id)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, pk=None):
        """获取单个情侣游戏详情"""
        try:
            sql = """
                SELECT 
                    id, 
                    name, 
                    description, 
                    game_type as type, 
                    difficulty, 
                    is_active as status, 
                    created_at, 
                    updated_at
                FROM game_game
                WHERE id = %s
            """
            
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                row = cursor.fetchone()
                
                if not row:
                    return Response({'error': '游戏不存在'}, status=status.HTTP_404_NOT_FOUND)
                
                columns = [col[0] for col in cursor.description]
                game = dict(zip(columns, row))
            
            # 转换status字段格式和时间格式
            game['status'] = 'active' if game['status'] else 'inactive'
            # 转换时间格式为年月日时分
            if game.get('created_at'):
                if isinstance(game['created_at'], datetime):
                    game['created_at'] = game['created_at'].strftime('%Y-%m-%d %H:%M')
            if game.get('updated_at'):
                if isinstance(game['updated_at'], datetime):
                    game['updated_at'] = game['updated_at'].strftime('%Y-%m-%d %H:%M')
            
            return Response(game)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, pk=None):
        """更新情侣游戏"""
        try:
            data = request.data
            
            # 将前端的status参数转换为is_active值
            is_active = 1 if data.get('status', 'active') == 'active' else 0
            
            sql = """
                UPDATE game_game SET
                    name = %s,
                    description = %s,
                    game_type = %s,
                    difficulty = %s,
                    is_active = %s,
                    updated_at = NOW()
                WHERE id = %s
            """
            
            params = [
                data.get('name'),
                data.get('description'),
                data.get('type'),
                data.get('difficulty'),
                is_active,
                pk
            ]
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                
                if cursor.rowcount == 0:
                    return Response({'error': '游戏不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            # 返回更新后的游戏
            return self.retrieve(request, pk)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, pk=None):
        """删除情侣游戏"""
        try:
            sql = "DELETE FROM game_game WHERE id = %s"
            
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                
                if cursor.rowcount == 0:
                    return Response({'error': '游戏不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            return Response({'message': '游戏删除成功'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
