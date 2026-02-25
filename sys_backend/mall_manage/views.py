from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from rest_framework.decorators import action


class ProductManagementViewSet(viewsets.ViewSet):
    """商品管理视图集 - 使用SQL操作"""
    
    def list(self, request):
        """获取商品列表"""
        try:
            # 获取筛选参数
            search = request.query_params.get('search', '')
            category = request.query_params.get('category', '')
            is_active = request.query_params.get('is_active', '')
            
            # 构建SQL查询
            sql = """
                SELECT 
                    id, 
                    name, 
                    description, 
                    price, 
                    old_price, 
                    main_image, 
                    detail_image, 
                    sku_image, 
                    rating, 
                    num_reviews, 
                    category_id, 
                    monthly_sales, 
                    product_stock, 
                    is_active, 
                    is_couple_product, 
                    is_new, 
                    created_at, 
                    updated_at
                FROM mall_product
            """
            
            # 添加筛选条件
            where_clauses = []
            params = []
            
            if search:
                where_clauses.append("(name LIKE %s OR description LIKE %s)")
                params.extend([f'%{search}%', f'%{search}%'])
            
            if category:
                where_clauses.append("category_id = %s")
                params.append(category)
            
            if is_active:
                where_clauses.append("is_active = %s")
                params.append(1 if is_active == 'true' else 0)
            
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            
            # 添加排序
            sql += " ORDER BY created_at DESC"
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                products = []
                from sys_LoveSync.storage import AliyunOSSStorage
                storage = AliyunOSSStorage()
                
                for row in cursor.fetchall():
                    product = dict(zip(columns, row))
                    # 转换状态字段为布尔值
                    product['is_active'] = bool(product['is_active'])
                    product['is_couple_product'] = bool(product['is_couple_product'])
                    product['is_new'] = bool(product['is_new'])
                    # 生成完整的图片URL（如果需要）
                    # 注意：mall_product表可能没有直接的image字段，需要根据实际表结构调整
                    products.append(product)
            
            return Response(products)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request):
        """创建商品"""
        try:
            import uuid
            data = request.data
            
            # 生成UUID作为商品ID（使用不带连字符的UUID格式，长度32）
            product_id = str(uuid.uuid4()).replace('-', '')
            
            sql = """
                INSERT INTO mall_product (
                    id, name, description, price, old_price, 
                    main_image, detail_image, sku_image, 
                    rating, num_reviews, category_id, monthly_sales, 
                    product_stock, is_active, is_couple_product, 
                    is_new, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """
            
            # 验证必填字段
            if not data.get('name') or not data.get('price') or not data.get('category_id'):
                return Response({'error': '商品名称、价格和分类是必填字段'}, status=status.HTTP_400_BAD_REQUEST)
            
            params = [
                product_id,
                data.get('name'),
                data.get('description', ''),
                float(data.get('price')),  # 转换为浮点数
                float(data.get('old_price', data.get('price'))),  # 转换为浮点数
                data.get('main_image', ''),
                data.get('detail_image', ''),
                data.get('sku_image', ''),
                data.get('rating', 0),
                data.get('num_reviews', 0),
                data.get('category_id'),
                data.get('monthly_sales', 0),
                data.get('product_stock', 0),
                1 if data.get('is_active', True) else 0,
                1 if data.get('is_couple_product', False) else 0,
                1 if data.get('is_new', True) else 0
            ]
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
            
            # 返回新创建的商品
            return self.retrieve(request, product_id)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, pk=None):
        """获取单个商品详情"""
        try:
            sql = """
                SELECT 
                    id, 
                    name, 
                    description, 
                    price, 
                    old_price, 
                    rating, 
                    num_reviews, 
                    category_id, 
                    monthly_sales, 
                    product_stock, 
                    is_active, 
                    is_couple_product, 
                    is_new, 
                    created_at, 
                    updated_at
                FROM mall_product
                WHERE id = %s
            """
            
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                row = cursor.fetchone()
                
                if not row:
                    return Response({'error': '商品不存在'}, status=status.HTTP_404_NOT_FOUND)
                
                columns = [col[0] for col in cursor.description]
                product = dict(zip(columns, row))
            
            return Response(product)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, pk=None):
        """更新商品"""
        try:
            data = request.data
            
            sql = """
                UPDATE mall_product SET
                    name = %s,
                    description = %s,
                    price = %s,
                    old_price = %s,
                    category_id = %s,
                    product_stock = %s,
                    is_active = %s,
                    is_couple_product = %s,
                    is_new = %s,
                    updated_at = NOW()
                WHERE id = %s
            """
            
            params = [
                data.get('name'),
                data.get('description', ''),
                data.get('price'),
                data.get('old_price', data.get('price')),
                data.get('category_id'),
                data.get('product_stock', 0),
                1 if data.get('is_active', True) else 0,
                1 if data.get('is_couple_product', False) else 0,
                1 if data.get('is_new', True) else 0,
                pk
            ]
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                
                if cursor.rowcount == 0:
                    return Response({'error': '商品不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            # 返回更新后的商品
            return self.retrieve(request, pk)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, pk=None):
        """删除商品"""
        try:
            sql = "DELETE FROM mall_product WHERE id = %s"
            
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                
                if cursor.rowcount == 0:
                    return Response({'error': '商品不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            return Response({'message': '商品删除成功'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取商城统计数据"""
        try:
            # 总商品数
            total_products_sql = "SELECT COUNT(*) FROM mall_product"
            
            # 总订单数
            total_orders_sql = "SELECT COUNT(*) FROM mall_order"
            
            # 今日销售（订单数）
            today_sales_sql = "SELECT COUNT(*) FROM mall_order WHERE DATE(created_at) = CURDATE()"
            
            with connection.cursor() as cursor:
                # 获取总商品数
                cursor.execute(total_products_sql)
                total_products = cursor.fetchone()[0] or 0
                
                # 获取总订单数
                cursor.execute(total_orders_sql)
                total_orders = cursor.fetchone()[0] or 0
                
                # 获取今日销售
                cursor.execute(today_sales_sql)
                today_sales = cursor.fetchone()[0] or 0
            
            return Response({
                'totalProducts': total_products,
                'totalOrders': total_orders,
                'todaySales': today_sales
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CategoryManagementViewSet(viewsets.ViewSet):
    """商品分类管理视图集 - 使用SQL操作"""
    
    def list(self, request):
        """获取商品分类列表"""
        try:
            # 获取筛选参数
            search = request.query_params.get('search', '')
            parent = request.query_params.get('parent', '')
            
            # 构建SQL查询
            sql = """
                SELECT 
                    id, 
                    name, 
                    parent_id, 
                    icon, 
                    sort, 
                    is_active, 
                    created_at
                FROM mall_category
            """
            
            # 添加筛选条件
            where_clauses = []
            params = []
            
            if search:
                where_clauses.append("name LIKE %s")
                params.append(f'%{search}%')
            
            if parent:
                where_clauses.append("parent_id = %s")
                params.append(parent)
            
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            
            # 添加排序
            sql += " ORDER BY sort, created_at DESC"
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                categories = []
                for row in cursor.fetchall():
                    category = dict(zip(columns, row))
                    # 转换状态字段为布尔值
                    category['is_active'] = bool(category['is_active'])
                    # 格式化时间字段
                    if category.get('created_at'):
                        category['created_at'] = category['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                    categories.append(category)
            
            return Response(categories)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request):
        """创建商品分类"""
        try:
            data = request.data
            
            sql = """
                INSERT INTO mall_category (
                    name, 
                    parent_id, 
                    icon, 
                    sort, 
                    is_active, 
                    created_at
                ) VALUES (%s, %s, %s, %s, %s, NOW())
            """
            
            # 处理parent_id字段，空字符串转换为None
            parent_id = data.get('parent_id')
            if parent_id == '' or parent_id == 'null':
                parent_id = None
            
            params = [
                data.get('name'),
                parent_id,
                data.get('icon', ''),
                data.get('sort', 0),
                1 if data.get('is_active', True) in (True, '1', 1) else 0
            ]
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                category_id = cursor.lastrowid
            
            # 返回新创建的分类
            response = self.retrieve(request, category_id)
            # 确保时间格式正确
            if response.data.get('created_at'):
                response.data['created_at'] = response.data['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            return response
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, pk=None):
        """获取单个商品分类详情"""
        try:
            sql = """
                SELECT 
                    id, 
                    name, 
                    parent_id, 
                    icon, 
                    sort, 
                    is_active, 
                    created_at
                FROM mall_category
                WHERE id = %s
            """
            
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                row = cursor.fetchone()
                
                if not row:
                    return Response({'error': '分类不存在'}, status=status.HTTP_404_NOT_FOUND)
                
                columns = [col[0] for col in cursor.description]
                category = dict(zip(columns, row))
                
                # 转换状态字段为布尔值
                category['is_active'] = bool(category['is_active'])
                # 格式化时间字段
                if category.get('created_at'):
                    category['created_at'] = category['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            return Response(category)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, pk=None):
        """更新商品分类"""
        try:
            data = request.data
            
            sql = """
                UPDATE mall_category SET
                    name = %s,
                    parent_id = %s,
                    icon = %s,
                    sort = %s,
                    is_active = %s
                WHERE id = %s
            """
            
            # 处理parent_id字段，空字符串转换为None
            parent_id = data.get('parent_id')
            if parent_id == '' or parent_id == 'null':
                parent_id = None
            
            params = [
                data.get('name'),
                parent_id,
                data.get('icon', ''),
                data.get('sort', 0),
                1 if data.get('is_active', True) in (True, '1', 1) else 0,
                pk
            ]
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                
                if cursor.rowcount == 0:
                    return Response({'error': '分类不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            # 返回更新后的分类
            return self.retrieve(request, pk)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, pk=None):
        """删除商品分类"""
        try:
            sql = "DELETE FROM mall_category WHERE id = %s"
            
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                
                if cursor.rowcount == 0:
                    return Response({'error': '分类不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            return Response({'message': '分类删除成功'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderManagementViewSet(viewsets.ViewSet):
    """订单管理视图集 - 使用SQL操作"""
    
    def list(self, request):
        """获取订单列表"""
        try:
            # 获取筛选参数
            order_number = request.query_params.get('order_number', '')
            status = request.query_params.get('status', '')
            user_id = request.query_params.get('user_id', '')
            
            # 构建SQL查询
            sql = """
                SELECT 
                    order_number, 
                    user_id, 
                    total_amount, 
                    status, 
                    payment_method, 
                    shipping_fee, 
                    logistics_company, 
                    logistics_no, 
                    remark, 
                    created_at, 
                    paid_at, 
                    shipped_at, 
                    delivered_at
                FROM mall_order
            """
            
            # 添加筛选条件
            where_clauses = []
            params = []
            
            if order_number:
                where_clauses.append("order_number LIKE %s")
                params.append(f'%{order_number}%')
            
            if status:
                where_clauses.append("status = %s")
                params.append(status)
            
            if user_id:
                where_clauses.append("user_id = %s")
                params.append(user_id)
            
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            
            # 添加排序
            sql += " ORDER BY created_at DESC"
            
            # 处理分页
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            offset = (page - 1) * page_size
            sql += f" LIMIT {page_size} OFFSET {offset}"
            
            with connection.cursor() as cursor:
                # 执行查询获取订单列表
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                orders = []
                for row in cursor.fetchall():
                    order = dict(zip(columns, row))
                    # 格式化时间字段
                    if order.get('created_at'):
                        order['created_at'] = order['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                    if order.get('paid_at'):
                        order['paid_at'] = order['paid_at'].strftime('%Y-%m-%d %H:%M:%S')
                    if order.get('shipped_at'):
                        order['shipped_at'] = order['shipped_at'].strftime('%Y-%m-%d %H:%M:%S')
                    if order.get('delivered_at'):
                        order['delivered_at'] = order['delivered_at'].strftime('%Y-%m-%d %H:%M:%S')
                    orders.append(order)
                
                # 获取总记录数
                count_sql = "SELECT COUNT(*) FROM mall_order"
                if where_clauses:
                    count_sql += " WHERE " + " AND ".join(where_clauses)
                cursor.execute(count_sql, params)
                total = cursor.fetchone()[0]
            
            return Response({
                'results': orders,
                'count': total
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, pk=None):
        """获取单个订单详情"""
        try:
            # 获取订单基本信息
            order_sql = """
                SELECT 
                    order_number, 
                    user_id, 
                    total_amount, 
                    status, 
                    payment_method, 
                    shipping_fee, 
                    logistics_company, 
                    logistics_no, 
                    remark, 
                    created_at, 
                    paid_at, 
                    shipped_at, 
                    delivered_at
                FROM mall_order
                WHERE order_number = %s
            """
            
            with connection.cursor() as cursor:
                cursor.execute(order_sql, [pk])
                order_row = cursor.fetchone()
                
                if not order_row:
                    return Response({'error': '订单不存在'}, status=status.HTTP_404_NOT_FOUND)
                
                order_columns = [col[0] for col in cursor.description]
                order = dict(zip(order_columns, order_row))
                
                # 格式化时间字段
                if order.get('created_at'):
                    order['created_at'] = order['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                if order.get('paid_at'):
                    order['paid_at'] = order['paid_at'].strftime('%Y-%m-%d %H:%M:%S')
                if order.get('shipped_at'):
                    order['shipped_at'] = order['shipped_at'].strftime('%Y-%m-%d %H:%M:%S')
                if order.get('delivered_at'):
                    order['delivered_at'] = order['delivered_at'].strftime('%Y-%m-%d %H:%M:%S')
                
                # 获取订单项（包含商品名称）
                items_sql = """
                    SELECT 
                        oi.id, 
                        oi.product_id, 
                        p.name as product_name, 
                        oi.sku_id, 
                        oi.quantity, 
                        oi.price, 
                        oi.total_price
                    FROM mall_orderitem oi
                    LEFT JOIN mall_product p ON oi.product_id = p.id
                    WHERE oi.order_id = (
                        SELECT id FROM mall_order WHERE order_number = %s
                    )
                """
                
                cursor.execute(items_sql, [pk])
                items_columns = [col[0] for col in cursor.description]
                items = [dict(zip(items_columns, row)) for row in cursor.fetchall()]
                
                order['items'] = items
            
            return Response(order)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, pk=None):
        """更新订单状态"""
        try:
            data = request.data
            status = data.get('status')
            
            if not status:
                return Response({'error': '请提供订单状态'}, status=status.HTTP_400_BAD_REQUEST)
            
            sql = """
                UPDATE mall_order SET
                    status = %s
                WHERE order_number = %s
            """
            
            with connection.cursor() as cursor:
                cursor.execute(sql, [status, pk])
                
                if cursor.rowcount == 0:
                    return Response({'error': '订单不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            # 返回更新后的订单
            return self.retrieve(request, pk)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentManagementViewSet(viewsets.ViewSet):
    """支付管理视图集 - 使用SQL操作"""
    
    def list(self, request):
        """获取支付记录列表"""
        try:
            # 获取筛选参数
            search = request.query_params.get('search', '')
            status = request.query_params.get('status', '')
            method = request.query_params.get('method', '')
            
            # 构建SQL查询
            sql = """
                SELECT 
                    payment_number, 
                    order_number, 
                    amount, 
                    refund_amount, 
                    method, 
                    status, 
                    transaction_id, 
                    refund_transaction_id, 
                    paid_at, 
                    refunded_at, 
                    created_at
                FROM mall_payment
            """
            
            # 添加筛选条件
            where_clauses = []
            params = []
            
            if search:
                where_clauses.append("(payment_number LIKE %s OR order_number LIKE %s)")
                params.extend([f'%{search}%', f'%{search}%'])
            
            if status:
                where_clauses.append("status = %s")
                params.append(status)
            
            if method:
                where_clauses.append("method = %s")
                params.append(method)
            
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            
            # 添加排序
            sql += " ORDER BY created_at DESC"
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                payments = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return Response(payments)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FlashSaleManagementViewSet(viewsets.ViewSet):
    """秒杀活动管理视图集 - 使用SQL操作"""
    
    def list(self, request):
        """获取秒杀活动列表"""
        try:
            # 获取筛选参数
            search = request.query_params.get('search', '')
            status = request.query_params.get('status', '')
            
            # 构建SQL查询
            sql = """
                SELECT 
                    id, 
                    name, 
                    start_time, 
                    end_time, 
                    status, 
                    description, 
                    need_countdown, 
                    is_vip_only, 
                    created_at
                FROM mall_flashsale
            """
            
            # 添加筛选条件
            where_clauses = []
            params = []
            
            if search:
                where_clauses.append("(name LIKE %s OR description LIKE %s)")
                params.extend([f'%{search}%', f'%{search}%'])
            
            if status:
                where_clauses.append("status = %s")
                params.append(1 if status == 'true' else 0)
            
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            
            # 添加排序
            sql += " ORDER BY start_time DESC"
            
            # 处理分页
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            offset = (page - 1) * page_size
            sql += f" LIMIT {page_size} OFFSET {offset}"
            
            with connection.cursor() as cursor:
                # 执行查询获取闪购活动列表
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                flash_sales = []
                for row in cursor.fetchall():
                    flash_sale = dict(zip(columns, row))
                    # 格式化时间字段
                    if flash_sale.get('start_time'):
                        flash_sale['start_time'] = flash_sale['start_time'].strftime('%Y-%m-%d %H:%M:%S')
                    if flash_sale.get('end_time'):
                        flash_sale['end_time'] = flash_sale['end_time'].strftime('%Y-%m-%d %H:%M:%S')
                    if flash_sale.get('created_at'):
                        flash_sale['created_at'] = flash_sale['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                    flash_sales.append(flash_sale)
                
                # 获取总记录数
                count_sql = "SELECT COUNT(*) FROM mall_flashsale"
                if where_clauses:
                    count_sql += " WHERE " + " AND ".join(where_clauses)
                cursor.execute(count_sql, params)
                total = cursor.fetchone()[0]
            
            return Response({
                'results': flash_sales,
                'count': total
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request):
        """创建秒杀活动"""
        try:
            data = request.data
            
            # 转换日期时间格式
            def format_datetime(datetime_str):
                if not datetime_str:
                    return datetime_str
                # 处理 ISO 格式的时间字符串，转换为 MySQL 支持的格式
                import datetime
                try:
                    # 尝试解析 ISO 格式
                    dt = datetime.datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    return datetime_str
            
            sql = """
                INSERT INTO mall_flashsale (
                    name, 
                    start_time, 
                    end_time, 
                    status, 
                    description, 
                    need_countdown, 
                    is_vip_only, 
                    created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """
            
            # 验证必填字段
            if not data.get('name') or not data.get('start_time') or not data.get('end_time'):
                return Response({'error': '活动名称和时间是必填字段'}, status=status.HTTP_400_BAD_REQUEST)
            
            params = [
                data.get('name'),
                format_datetime(data.get('start_time')),
                format_datetime(data.get('end_time')),
                1 if data.get('status', True) in (True, '1', 1) else 0,
                data.get('description', ''),
                1 if data.get('need_countdown', False) in (True, '1', 1) else 0,
                1 if data.get('is_vip_only', False) in (True, '1', 1) else 0
            ]
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                flash_sale_id = cursor.lastrowid
            
            # 返回新创建的闪购活动
            return self.retrieve(request, flash_sale_id)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, pk=None):
        """获取单个秒杀活动详情"""
        try:
            sql = """
                SELECT 
                    id, 
                    name, 
                    start_time, 
                    end_time, 
                    status, 
                    description, 
                    need_countdown, 
                    is_vip_only, 
                    created_at
                FROM mall_flashsale
                WHERE id = %s
            """
            
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                row = cursor.fetchone()
                
                if not row:
                    return Response({'error': '闪购活动不存在'}, status=status.HTTP_404_NOT_FOUND)
                
                columns = [col[0] for col in cursor.description]
                flash_sale = dict(zip(columns, row))
            
            return Response(flash_sale)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, pk=None):
        """更新秒杀活动"""
        try:
            data = request.data
            
            # 转换日期时间格式
            def format_datetime(datetime_str):
                if not datetime_str:
                    return datetime_str
                # 处理 ISO 格式的时间字符串，转换为 MySQL 支持的格式
                import datetime
                try:
                    # 尝试解析 ISO 格式
                    dt = datetime.datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    return datetime_str
            
            sql = """
                UPDATE mall_flashsale SET
                    name = %s,
                    start_time = %s,
                    end_time = %s,
                    status = %s,
                    description = %s,
                    need_countdown = %s,
                    is_vip_only = %s
                WHERE id = %s
            """
            
            # 验证必填字段
            if not data.get('name') or not data.get('start_time') or not data.get('end_time'):
                return Response({'error': '活动名称和时间是必填字段'}, status=status.HTTP_400_BAD_REQUEST)
            
            params = [
                data.get('name'),
                format_datetime(data.get('start_time')),
                format_datetime(data.get('end_time')),
                1 if data.get('status', True) in (True, '1', 1) else 0,
                data.get('description', ''),
                1 if data.get('need_countdown', False) in (True, '1', 1) else 0,
                1 if data.get('is_vip_only', False) in (True, '1', 1) else 0,
                pk
            ]
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                
                if cursor.rowcount == 0:
                    return Response({'error': '闪购活动不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            # 返回更新后的闪购活动
            return self.retrieve(request, pk)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, pk=None):
        """删除秒杀活动"""
        try:
            sql = "DELETE FROM mall_flashsale WHERE id = %s"
            
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                
                if cursor.rowcount == 0:
                    return Response({'error': '闪购活动不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            return Response({'message': '闪购活动删除成功'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CouponManagementViewSet(viewsets.ViewSet):
    """优惠券管理视图集 - 使用SQL操作"""
    
    def list(self, request):
        """获取优惠券列表"""
        try:
            # 获取筛选参数
            search = request.query_params.get('search', '')
            type = request.query_params.get('type', '')
            is_active = request.query_params.get('is_active', '')
            
            # 构建SQL查询
            sql = """
                SELECT 
                    id, 
                    name, 
                    type, 
                    value, 
                    min_spend, 
                    start_time, 
                    end_time, 
                    total_quantity, 
                    remaining_quantity, 
                    is_active, 
                    created_at
                FROM mall_coupon
            """
            
            # 添加筛选条件
            where_clauses = []
            params = []
            
            if search:
                where_clauses.append("name LIKE %s")
                params.append(f'%{search}%')
            
            if type:
                where_clauses.append("type = %s")
                params.append(type)
            
            if is_active:
                where_clauses.append("is_active = %s")
                params.append(1 if is_active == 'true' else 0)
            
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            
            # 添加排序
            sql += " ORDER BY created_at DESC"
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                coupons = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # 处理分页
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            offset = (page - 1) * page_size
            sql += f" LIMIT {page_size} OFFSET {offset}"
            
            with connection.cursor() as cursor:
                # 执行查询获取优惠券列表
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                coupons = []
                for row in cursor.fetchall():
                    coupon = dict(zip(columns, row))
                    # 格式化时间字段
                    if coupon.get('start_time'):
                        coupon['start_time'] = coupon['start_time'].strftime('%Y-%m-%d %H:%M:%S')
                    if coupon.get('end_time'):
                        coupon['end_time'] = coupon['end_time'].strftime('%Y-%m-%d %H:%M:%S')
                    if coupon.get('created_at'):
                        coupon['created_at'] = coupon['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                    coupons.append(coupon)
                
                # 获取总记录数
                count_sql = "SELECT COUNT(*) FROM mall_coupon"
                if where_clauses:
                    count_sql += " WHERE " + " AND ".join(where_clauses)
                cursor.execute(count_sql, params)
                total = cursor.fetchone()[0]
            
            return Response({
                'results': coupons,
                'count': total
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request):
        """创建优惠券"""
        try:
            data = request.data
            
            # 转换日期时间格式
            def format_datetime(datetime_str):
                if not datetime_str:
                    return datetime_str
                # 处理 ISO 格式的时间字符串，转换为 MySQL 支持的格式
                import datetime
                try:
                    # 尝试解析 ISO 格式
                    dt = datetime.datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    return datetime_str
            
            sql = """
                INSERT INTO mall_coupon (
                    name, 
                    type, 
                    value, 
                    min_spend, 
                    start_time, 
                    end_time, 
                    total_quantity, 
                    remaining_quantity, 
                    is_active, 
                    created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            
            # 验证必填字段
            if not data.get('name') or not data.get('type') or not data.get('value') or not data.get('total_quantity'):
                return Response({'error': '优惠券名称、类型、金额和总数量是必填字段'}, status=status.HTTP_400_BAD_REQUEST)
            
            total_quantity = int(data.get('total_quantity'))
            
            params = [
                data.get('name'),
                data.get('type'),
                float(data.get('value')),
                float(data.get('min_spend', 0)),
                format_datetime(data.get('start_time')),
                format_datetime(data.get('end_time')),
                total_quantity,
                total_quantity,  # 剩余数量初始值等于总数量
                1 if data.get('is_active', True) in (True, '1', 1) else 0
            ]
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                coupon_id = cursor.lastrowid
            
            # 返回新创建的优惠券
            return self.retrieve(request, coupon_id)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, pk=None):
        """获取单个优惠券详情"""
        try:
            sql = """
                SELECT 
                    id, 
                    name, 
                    type, 
                    value, 
                    min_spend, 
                    start_time, 
                    end_time, 
                    total_quantity, 
                    remaining_quantity, 
                    is_active, 
                    created_at
                FROM mall_coupon
                WHERE id = %s
            """
            
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                row = cursor.fetchone()
                
                if not row:
                    return Response({'error': '优惠券不存在'}, status=status.HTTP_404_NOT_FOUND)
                
                columns = [col[0] for col in cursor.description]
                coupon = dict(zip(columns, row))
                
                # 格式化时间字段
                if coupon.get('start_time'):
                    coupon['start_time'] = coupon['start_time'].strftime('%Y-%m-%d %H:%M:%S')
                if coupon.get('end_time'):
                    coupon['end_time'] = coupon['end_time'].strftime('%Y-%m-%d %H:%M:%S')
                if coupon.get('created_at'):
                    coupon['created_at'] = coupon['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            return Response(coupon)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, pk=None):
        """更新优惠券"""
        try:
            data = request.data
            
            # 转换日期时间格式
            def format_datetime(datetime_str):
                if not datetime_str:
                    return datetime_str
                # 处理 ISO 格式的时间字符串，转换为 MySQL 支持的格式
                import datetime
                try:
                    # 尝试解析 ISO 格式
                    dt = datetime.datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    return datetime_str
            
            sql = """
                UPDATE mall_coupon SET
                    name = %s,
                    type = %s,
                    value = %s,
                    min_spend = %s,
                    start_time = %s,
                    end_time = %s,
                    total_quantity = %s,
                    is_active = %s
                WHERE id = %s
            """
            
            # 验证必填字段
            if not data.get('name') or not data.get('type') or not data.get('value') or not data.get('total_quantity'):
                return Response({'error': '优惠券名称、类型、金额和总数量是必填字段'}, status=status.HTTP_400_BAD_REQUEST)
            
            params = [
                data.get('name'),
                data.get('type'),
                float(data.get('value')),
                float(data.get('min_spend', 0)),
                format_datetime(data.get('start_time')),
                format_datetime(data.get('end_time')),
                int(data.get('total_quantity')),
                1 if data.get('is_active', True) in (True, '1', 1) else 0,
                pk
            ]
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                
                if cursor.rowcount == 0:
                    return Response({'error': '优惠券不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            # 返回更新后的优惠券
            return self.retrieve(request, pk)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, pk=None):
        """删除优惠券"""
        try:
            sql = "DELETE FROM mall_coupon WHERE id = %s"
            
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                
                if cursor.rowcount == 0:
                    return Response({'error': '优惠券不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            return Response({'message': '优惠券删除成功'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BannerManagementViewSet(viewsets.ViewSet):
    """首页轮播图管理视图集 - 使用SQL操作"""
    
    def list(self, request):
        """获取首页轮播图列表"""
        try:
            # 获取筛选参数
            search = request.query_params.get('search', '')
            
            # 构建SQL查询
            sql = """
                SELECT 
                    id, 
                    title, 
                    link, 
                    image, 
                    sort, 
                    is_active, 
                    created_at
                FROM mall_homebanner
            """
            
            # 添加筛选条件
            where_clauses = []
            params = []
            
            if search:
                where_clauses.append("title LIKE %s")
                params.append(f'%{search}%')
            
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            
            # 添加排序
            sql += " ORDER BY sort, created_at DESC"
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                banners = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # 处理分页
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            offset = (page - 1) * page_size
            sql += f" LIMIT {page_size} OFFSET {offset}"
            
            with connection.cursor() as cursor:
                # 执行查询获取Banner列表
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                banners = []
                for row in cursor.fetchall():
                    banner = dict(zip(columns, row))
                    # 格式化时间字段
                    if banner.get('created_at'):
                        banner['created_at'] = banner['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                    banners.append(banner)
                
                # 获取总记录数
                count_sql = "SELECT COUNT(*) FROM mall_homebanner"
                if where_clauses:
                    count_sql += " WHERE " + " AND ".join(where_clauses)
                cursor.execute(count_sql, params)
                total = cursor.fetchone()[0]
            
            return Response({
                'results': banners,
                'count': total
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request):
        """创建Banner"""
        try:
            data = request.data
            
            sql = """
                INSERT INTO mall_homebanner (
                    title, 
                    link, 
                    image, 
                    sort, 
                    is_active, 
                    created_at
                ) VALUES (%s, %s, %s, %s, %s, NOW())
            """
            
            # 验证必填字段
            if not data.get('title'):
                return Response({'error': 'Banner名称是必填字段'}, status=status.HTTP_400_BAD_REQUEST)
            
            params = [
                data.get('title'),
                data.get('link', ''),
                data.get('image', ''),
                int(data.get('sort', 0)),
                1 if data.get('is_active', True) in (True, '1', 1) else 0
            ]
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                banner_id = cursor.lastrowid
            
            # 返回新创建的Banner
            return self.retrieve(request, banner_id)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, pk=None):
        """获取单个Banner详情"""
        try:
            sql = """
                SELECT 
                    id, 
                    title, 
                    link, 
                    image, 
                    sort, 
                    is_active, 
                    created_at
                FROM mall_homebanner
                WHERE id = %s
            """
            
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                row = cursor.fetchone()
                
                if not row:
                    return Response({'error': 'Banner不存在'}, status=status.HTTP_404_NOT_FOUND)
                
                columns = [col[0] for col in cursor.description]
                banner = dict(zip(columns, row))
                
                # 格式化时间字段
                if banner.get('created_at'):
                    banner['created_at'] = banner['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            return Response(banner)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, pk=None):
        """更新Banner"""
        try:
            data = request.data
            
            sql = """
                UPDATE mall_homebanner SET
                    title = %s,
                    link = %s,
                    image = %s,
                    sort = %s,
                    is_active = %s
                WHERE id = %s
            """
            
            # 验证必填字段
            if not data.get('title'):
                return Response({'error': 'Banner名称是必填字段'}, status=status.HTTP_400_BAD_REQUEST)
            
            params = [
                data.get('title'),
                data.get('link', ''),
                data.get('image', ''),
                int(data.get('sort', 0)),
                1 if data.get('is_active', True) in (True, '1', 1) else 0,
                pk
            ]
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                
                if cursor.rowcount == 0:
                    return Response({'error': 'Banner不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            # 返回更新后的Banner
            return self.retrieve(request, pk)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, pk=None):
        """删除Banner"""
        try:
            sql = "DELETE FROM mall_homebanner WHERE id = %s"
            
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                
                if cursor.rowcount == 0:
                    return Response({'error': 'Banner不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            return Response({'message': 'Banner删除成功'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AddressManagementViewSet(viewsets.ViewSet):
    """收货地址管理视图集 - 使用SQL操作"""
    
    def list(self, request):
        """获取收货地址列表"""
        try:
            # 获取筛选参数
            user_id = request.query_params.get('user_id', '')
            recipient = request.query_params.get('recipient', '')
            
            # 构建SQL查询
            sql = """
                SELECT 
                    id, 
                    user_id, 
                    recipient, 
                    phone, 
                    province, 
                    city, 
                    district, 
                    detail_address, 
                    is_default, 
                    created_at, 
                    updated_at
                FROM mall_address
            """
            
            # 添加筛选条件
            where_clauses = []
            params = []
            
            if user_id:
                where_clauses.append("user_id = %s")
                params.append(user_id)
            
            if recipient:
                where_clauses.append("recipient LIKE %s")
                params.append(f'%{recipient}%')
            
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            
            # 添加排序
            sql += " ORDER BY is_default DESC, updated_at DESC"
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                addresses = []
                for row in cursor.fetchall():
                    address = dict(zip(columns, row))
                    # 格式化时间字段
                    if address.get('created_at'):
                        address['created_at'] = address['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                    if address.get('updated_at'):
                        address['updated_at'] = address['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
                    addresses.append(address)
            
            return Response(addresses)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, pk=None):
        """获取单个收货地址详情"""
        try:
            sql = """
                SELECT 
                    id, 
                    user_id, 
                    recipient, 
                    phone, 
                    province, 
                    city, 
                    district, 
                    detail_address, 
                    is_default, 
                    created_at, 
                    updated_at
                FROM mall_address
                WHERE id = %s
            """
            
            with connection.cursor() as cursor:
                cursor.execute(sql, [pk])
                row = cursor.fetchone()
                
                if not row:
                    return Response({'error': '地址不存在'}, status=status.HTTP_404_NOT_FOUND)
                
                columns = [col[0] for col in cursor.description]
                address = dict(zip(columns, row))
                
                # 格式化时间字段
                if address.get('created_at'):
                    address['created_at'] = address['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                if address.get('updated_at'):
                    address['updated_at'] = address['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            return Response(address)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, pk=None):
        """删除收货地址"""
        try:
            # 检查是否有相关订单
            check_sql = "SELECT COUNT(*) FROM mall_order WHERE address_id = %s"
            
            with connection.cursor() as cursor:
                cursor.execute(check_sql, [pk])
                count = cursor.fetchone()[0]
                
                if count > 0:
                    return Response({'error': '该地址正在被订单使用，无法删除'}, status=status.HTTP_400_BAD_REQUEST)
                
                # 执行删除操作
                delete_sql = "DELETE FROM mall_address WHERE id = %s"
                cursor.execute(delete_sql, [pk])
                
                if cursor.rowcount == 0:
                    return Response({'error': '地址不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            return Response({'message': '地址删除成功'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
