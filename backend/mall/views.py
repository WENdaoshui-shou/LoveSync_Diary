from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
from .models import Product, CartItem
from .serializers import ProductSerializer, CartItemSerializer, CartItemCreateSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """商品视图集"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取商品列表，支持按类别筛选"""
        queryset = self.queryset
        category = self.request.query_params.get('category')
        
        if category:
            queryset = queryset.filter(category=category)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """获取所有商品类别"""
        categories = self.queryset.values_list('category', flat=True).distinct()
        return Response({'categories': list(categories)})


class CartItemViewSet(viewsets.ModelViewSet):
    """购物车商品视图集"""
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的购物车商品"""
        return self.queryset.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """根据请求方法选择序列化器"""
        if self.action == 'create':
            return CartItemCreateSerializer
        return CartItemSerializer
    
    def perform_create(self, serializer):
        """创建购物车商品"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def count(self, request):
        """获取购物车商品数量"""
        count = self.get_queryset().count()
        return Response({'count': count})
    
    @action(detail=True, methods=['put'])
    def update_quantity(self, request, pk=None):
        """更新购物车商品数量"""
        cart_item = self.get_object()
        quantity = request.data.get('quantity')
        
        if quantity is not None:
            cart_item.quantity = quantity
            cart_item.save()
            return Response({'quantity': cart_item.quantity})
        return Response({'error': '缺少quantity参数'}, status=status.HTTP_400_BAD_REQUEST)


# 推荐商品装饰器
def recommend_view(func):
    def _wrapper(request, *args, **kwargs):
        # 从cookie中获取用户访问的所有商品id
        c_id = request.COOKIES.get('rem', '')

        # 存放用户访问商品的id列表，使用逗号分隔
        visited_ids = [gid for gid in c_id.split(',') if gid.strip()]

        # 构建推荐商品列表（这里使用简单逻辑，实际项目中可根据需求优化）
        recommended_products = []
        if visited_ids:
            # 从用户访问过的商品中推荐前3个（如果有）
            recommended_products = Product.objects.filter(id__in=visited_ids[:5])

        # 将推荐商品添加到请求对象中
        request.recommended_products = recommended_products

        # 调用原视图函数
        response = func(request, *args, **kwargs)

        # 获取当前查看的商品ID（如果有）
        current_product_id = request.GET.get('product_id')
        if current_product_id and current_product_id not in visited_ids:
            # 将当前商品ID添加到访问历史的最前面
            visited_ids.insert(0, current_product_id)
            # 限制历史记录长度为10个商品
            if len(visited_ids) > 10:
                visited_ids = visited_ids[:10]
            # 更新cookie
            response.set_cookie('rem', ','.join(visited_ids), max_age=24 * 60 * 60)

        return response

    return _wrapper


# 购物商城页面
@login_required
@recommend_view
def mall(request, recommended_products=None):
    products = Product.objects.all()

    # 如果装饰器提供了推荐商品，则使用它们
    if recommended_products is None:
        # 否则使用默认的随机推荐
        recommended_products = Product.objects.order_by('?')[:5]

    hot_products = Product.objects.order_by('-monthly_sales')[:3]

    return render(request, 'mall.html', {
        'products': products,
        'recommended_products': recommended_products,
        'hot_products': hot_products
    })


# 商品详情页面
@recommend_view
def product_detail(request, product_id):
    """商品详情视图"""
    product = get_object_or_404(Product, id=product_id)

    # 从请求对象中获取推荐商品
    recommended_products = getattr(request, 'recommended_products', [])
    if not recommended_products:
        recommended_products = Product.objects.order_by('-rating')[:5]

    hot_products = Product.objects.order_by('-monthly_sales')[:3]

    return render(request, 'product_detail.html', {
        'product': product,
        'recommended_products': recommended_products,
        'hot_products': hot_products
    })


# 添加商品到购物车
@login_required
@require_POST
def add_to_cart(request):
    try:
        # 1. 获取请求参数
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))

        # 2. 验证参数有效性
        if not product_id or quantity <= 0:
            return JsonResponse({
                'status': 'error',
                'message': '无效的商品ID或数量'
            }, status=400)

        # 3. 获取商品并验证库存
        product = get_object_or_404(Product, id=product_id)
        if product.product_stock < quantity:
            return JsonResponse({
                'status': 'error',
                'message': f'库存不足，当前仅剩余{product.product_stock}件'
            }, status=400)

        # 4. 同步数据库：创建或更新购物车记录
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            # 已存在则累加数量
            cart_item.quantity += quantity
            cart_item.save()

        # 5. 同步缓存：更新Redis缓存（提升读取速度）
        user_id = request.user.id
        cart_key = f'user_cart:{user_id}'  # 缓存键格式：user_cart:用户ID
        cart = cache.get(cart_key, {})  # 从缓存获取当前购物车

        # 更新缓存中的商品信息
        cart[str(product_id)] = {
            'id': product_id,
            'name': product.name,
            'price': str(product.price),
            'quantity': cart_item.quantity,
        }
        cache.set(cart_key, cart, timeout=86400)  # 缓存1天

        # 6. 扣减商品库存
        product.product_stock -= quantity
        product.save()

        return JsonResponse({
            'status': 'success',
            'message': f'已将{product.name}加入购物车',
            'cart_count': sum(item['quantity'] for item in cart.values())  # 购物车总数量
        })

    except ValueError:
        return JsonResponse({
            'status': 'error',
            'message': '数量必须是有效数字'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'操作失败：{str(e)}'
        }, status=500)


# 获取购物车商品总数
@login_required
def cart_count(request):
    user_id = request.user.id
    cart_key = f'user_cart:{user_id}'
    cart = cache.get(cart_key, {})
    count = sum(item['quantity'] for item in cart.values())
    return JsonResponse({'count': count})


# 购物车页面
@login_required
def mallcart(request):
    user_id = request.user.id
    cart_key = f'user_cart:{user_id}'
    cart = cache.get(cart_key)
    # 缓存失效时从数据库加载并更新缓存
    if cart:
        cart_items = CartItem.objects.filter(user=request.user).select_related('product')
        cart = {
            str(item.product.id): {
                'name': item.product.name,
                'price': str(item.product.price),
                'quantity': item.quantity,
                'image': item.product.image.url
            } for item in cart_items
        }
        print(cart)
        cache.set(cart_key, cart, timeout=86400)

    return render(request, 'mallcart.html', {'cart_items': cart})


# 更新购物车
@login_required
def update_cart(request):
    if request.method == 'POST':
        try:
            # 解析前端发送的JSON数据
            import json
            cart_data = json.loads(request.body)
            user = request.user
            cart_key = f'user_cart:{user.id}'

            # 获取用户当前所有购物车项
            existing_items = {
                item.product.id: item
                for item in CartItem.objects.filter(user=user)
            }

            # 处理前端发送的每个商品
            for product_id, item_data in cart_data.items():
                try:
                    product_id_int = int(product_id)
                    product = Product.objects.get(id=product_id_int)

                    # 检查商品是否已在购物车中
                    if product_id_int in existing_items:
                        # 更新现有商品数量
                        cart_item = existing_items[product_id_int]
                        cart_item.quantity = item_data['quantity']
                        cart_item.save()
                        del existing_items[product_id_int]
                    else:
                        # 添加新商品到购物车
                        CartItem.objects.create(
                            user=user,
                            product=product,
                            quantity=item_data['quantity']
                        )
                except (ValueError, Product.DoesNotExist):
                    # 忽略无效的商品ID
                    continue

            # 删除前端购物车中已不存在的商品
            for remaining_item in existing_items.values():
                remaining_item.delete()

            # 更新缓存
            updated_items = CartItem.objects.filter(user=user).select_related('product')
            updated_cart = {
                str(item.product.id): {
                    'name': item.product.name,
                    'price': str(item.product.price),
                    'quantity': item.quantity,
                    'image': item.product.image.url
                } for item in updated_items
            }
            cache.set(cart_key, updated_cart, timeout=86400)

            return JsonResponse({
                'success': True,
                'message': '购物车已更新',
                'item_count': updated_items.count()
            })

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': '无效的JSON数据'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    # 处理非POST请求
    return JsonResponse({'success': False, 'message': '仅支持POST请求'}, status=405)


# 收藏页面
@login_required
def mallmark(request):
    return render(request, 'mallmark.html')


# 结算视图
@login_required
def checkout(request, product_id=None):
    user_id = request.user.id
    cart_key = f'user_cart:{user_id}'
    cart = cache.get(cart_key, {})
    return render(request, 'checkout.html', {'cart_items': cart, 'product_id': product_id})