from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.db import connection


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
                products = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return Response(products)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request):
        """创建商品"""
        try:
            data = request.data
            
            sql = """
                INSERT INTO mall_product (
                    name, description, price, old_price, 
                    category_id, product_stock, is_active, 
                    is_couple_product, is_new, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
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
                1 if data.get('is_new', True) else 0
            ]
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                product_id = cursor.lastrowid
            
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
                categories = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
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
                    sort, 
                    is_active, 
                    created_at
                ) VALUES (%s, %s, %s, %s, NOW())
            """
            
            params = [
                data.get('name'),
                data.get('parent_id', None),
                data.get('sort', 0),
                1 if data.get('is_active', True) else 0
            ]
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                category_id = cursor.lastrowid
            
            # 返回新创建的分类
            return self.retrieve(request, category_id)
            
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
                    sort = %s,
                    is_active = %s
                WHERE id = %s
            """
            
            params = [
                data.get('name'),
                data.get('parent_id', None),
                data.get('sort', 0),
                1 if data.get('is_active', True) else 0,
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
            search = request.query_params.get('search', '')
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
            
            if search:
                where_clauses.append("order_number LIKE %s")
                params.append(f'%{search}%')
            
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
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                orders = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return Response(orders)
            
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
                
                # 获取订单项
                items_sql = """
                    SELECT 
                        id, 
                        product_id, 
                        sku_id, 
                        quantity, 
                        price, 
                        total_price
                    FROM mall_orderitem
                    WHERE order_id = (
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
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                flash_sales = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return Response(flash_sales)
            
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
            
            return Response(coupons)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BannerManagementViewSet(viewsets.ViewSet):
    """首页轮播图管理视图集 - 使用SQL操作"""
    
    def list(self, request):
        """获取首页轮播图列表"""
        try:
            # 构建SQL查询
            sql = """
                SELECT 
                    id, 
                    title, 
                    link, 
                    sort, 
                    is_active, 
                    created_at
                FROM mall_homebanner
                ORDER BY sort, created_at DESC
            """
            
            with connection.cursor() as cursor:
                cursor.execute(sql)
                columns = [col[0] for col in cursor.description]
                banners = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return Response(banners)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AddressManagementViewSet(viewsets.ViewSet):
    """收货地址管理视图集 - 使用SQL操作"""
    
    def list(self, request):
        """获取收货地址列表"""
        try:
            # 获取筛选参数
            user_id = request.query_params.get('user_id', '')
            
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
            
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            
            # 添加排序
            sql += " ORDER BY is_default DESC, updated_at DESC"
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                addresses = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return Response(addresses)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
