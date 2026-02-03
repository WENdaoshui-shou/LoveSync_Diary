from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.http import JsonResponse, HttpResponse
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.db.models import F, Avg, Sum, Case, When, IntegerField, FloatField
import json
import hashlib
import time
import uuid
import os

from .models import (
    Category, Product, ProductSKU, CartItem, Address, Order, OrderItem,
    Payment, FlashSale, FlashSaleProduct, Coupon, UserCoupon, Logistics,
    ProductMark, HomeBanner, ProductTag, ProductTagRelation, UserBehavior, RefundApplication, ProductReview
)
from .serializers import (
    CategorySerializer, ProductSerializer, ProductSKUSerializer, CartItemSerializer, CartItemCreateSerializer,
    AddressSerializer, OrderSerializer, OrderItemSerializer, PaymentSerializer, PaymentCreateSerializer,
    FlashSaleSerializer, FlashSaleProductSerializer, CouponSerializer, UserCouponSerializer, LogisticsSerializer,
    ProductMarkSerializer, HomeBannerSerializer, ProductTagSerializer, ProductTagRelationSerializer,
    UserBehaviorSerializer, RefundApplicationSerializer, OrderCreateSerializer, CouponApplySerializer,
    FlashSalePurchaseSerializer
)


# API视图集

class CategoryViewSet(viewsets.ModelViewSet):
    """商品分类视图集"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """获取分类树形结构"""
        categories = self.queryset
        category_tree = []

        def build_tree(parent_id=None):
            """递归构建分类树"""
            children = []
            for category in categories.filter(parent_id=parent_id):
                child = {
                    'id': category.id,
                    'name': category.name,
                    'children': build_tree(category.id)
                }
                children.append(child)
            return children

        category_tree = build_tree()
        return Response({'categories': category_tree})


class ProductViewSet(viewsets.ModelViewSet):
    """商品视图集"""
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """获取商品列表，支持按类别、标签、情侣款筛选"""
        queryset = self.queryset
        category_id = self.request.query_params.get('category')
        tag_id = self.request.query_params.get('tag')
        is_couple = self.request.query_params.get('is_couple')

        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if tag_id:
            queryset = queryset.filter(tags__tag_id=tag_id)
        if is_couple == 'true':
            queryset = queryset.filter(is_couple_product=True)

        return queryset

    @action(detail=False, methods=['get'])
    def hot(self, request):
        """获取热门商品"""
        hot_products = self.queryset.order_by('-monthly_sales')[:10]
        serializer = self.get_serializer(hot_products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def couple(self, request):
        """获取情侣款商品"""
        couple_products = self.queryset.filter(is_couple_product=True)[:10]
        serializer = self.get_serializer(couple_products, many=True)
        return Response(serializer.data)


class ProductSKUViewSet(viewsets.ModelViewSet):
    """商品规格视图集"""
    queryset = ProductSKU.objects.filter(is_active=True)
    serializer_class = ProductSKUSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def by_product(self, request):
        """根据商品ID获取规格"""
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response({'error': '缺少product_id参数'}, status=status.HTTP_400_BAD_REQUEST)
        skus = self.queryset.filter(product_id=product_id)
        serializer = self.get_serializer(skus, many=True)
        return Response(serializer.data)


class CartItemViewSet(viewsets.ModelViewSet):
    """购物车项视图集"""
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """获取当前用户的购物车项"""
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """根据请求方法选择序列化器"""
        if self.action == 'create':
            return CartItemCreateSerializer
        return CartItemSerializer

    def perform_create(self, serializer):
        """创建购物车项"""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def count(self, request):
        """获取购物车商品数量"""
        count = self.get_queryset().count()
        return Response({'count': count})

    @action(detail=False, methods=['get'])
    def selected(self, request):
        """获取选中的购物车项"""
        selected_items = self.get_queryset().filter(selected=True)
        serializer = self.get_serializer(selected_items, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['put'])
    def update_quantity(self, request, pk=None):
        """更新购物车项数量"""
        cart_item = self.get_object()
        quantity = request.data.get('quantity')

        if quantity is not None:
            cart_item.quantity = quantity
            cart_item.save()
            return Response({'quantity': cart_item.quantity})
        return Response({'error': '缺少quantity参数'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'])
    def toggle_selected(self, request, pk=None):
        """切换购物车项选中状态"""
        cart_item = self.get_object()
        cart_item.selected = not cart_item.selected
        cart_item.save()
        return Response({'selected': cart_item.selected})


class AddressViewSet(viewsets.ModelViewSet):
    """收货地址视图集"""
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """获取当前用户的收货地址"""
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """创建收货地址"""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['put'])
    def set_default(self, request, pk=None):
        """设置默认地址"""
        address = self.get_object()
        address.is_default = True
        address.save()
        return Response({'is_default': True})


class OrderViewSet(viewsets.ModelViewSet):
    """订单视图集"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """获取当前用户的订单"""
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """根据请求方法选择序列化器"""
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        """创建订单"""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['put'])
    def cancel(self, request, pk=None):
        """取消订单"""
        order = self.get_object()
        if order.status == 'pending':
            order.status = 'cancelled'
            order.save()
            return Response({'status': 'cancelled'})
        return Response({'error': '订单状态不允许取消'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'])
    def confirm_receipt(self, request, pk=None):
        """确认收货"""
        order = self.get_object()
        if order.status == 'shipped':
            order.status = 'delivered'
            order.delivered_at = timezone.now()
            order.save()
            return Response({'status': 'delivered'})
        return Response({'error': '订单状态不允许确认收货'}, status=status.HTTP_400_BAD_REQUEST)


class PaymentViewSet(viewsets.ModelViewSet):
    """支付视图集"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """获取当前用户的支付记录"""
        return self.queryset.filter(order__user=self.request.user)

    def get_serializer_class(self):
        """根据请求方法选择序列化器"""
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer

    @action(detail=True, methods=['put'])
    def refund(self, request, pk=None):
        """申请退款"""
        payment = self.get_object()
        if payment.status == 'success':
            refund_amount = request.data.get('refund_amount', payment.amount)
            payment.refund_amount = refund_amount
            payment.status = 'refunded'
            payment.refunded_at = timezone.now()
            payment.save()

            # 更新订单状态
            order = payment.order
            order.status = 'refunded'
            order.save()

            return Response({'status': 'refunded', 'refund_amount': refund_amount})
        return Response({'error': '支付状态不允许退款'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def create_payment(self, request):
        """创建支付订单"""
        try:
            order_id = request.data.get('order_id')
            payment_method = request.data.get('payment_method')
            amount = request.data.get('amount')

            if not order_id or not payment_method or not amount:
                return Response({'error': '缺少必要参数'}, status=status.HTTP_400_BAD_REQUEST)

            # 验证订单
            order = get_object_or_404(Order, id=order_id, user=request.user)
            if order.status != 'pending':
                return Response({'error': '订单状态不允许支付'}, status=status.HTTP_400_BAD_REQUEST)

            # 创建支付记录
            payment = Payment.objects.create(
                order=order,
                amount=amount,
                method=payment_method,
                status='pending'
            )

            # 模拟支付接口调用
            if payment_method == 'wechat':
                # 微信支付模拟
                pay_url = f"/api/mall/payments/{payment.id}/wechat-pay"
            elif payment_method == 'alipay':
                # 支付宝模拟
                pay_url = f"/api/mall/payments/{payment.id}/alipay"
            else:
                # 银行卡支付模拟
                pay_url = f"/api/mall/payments/{payment.id}/card-pay"

            return Response({
                'success': True,
                'payment_id': payment.id,
                'pay_url': pay_url,
                'order_number': order.order_number
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def wechat_pay(self, request, pk=None):
        """微信支付模拟"""
        payment = self.get_object()
        
        # 模拟微信支付接口返回
        return Response({
            'success': True,
            'pay_url': 'weixin://pay?prepay_id=wx202501301234567890',
            'qr_code': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==',
            'payment_id': payment.id
        })

    @action(detail=True, methods=['get'])
    def alipay(self, request, pk=None):
        """支付宝模拟"""
        payment = self.get_object()
        
        # 模拟支付宝接口返回
        return Response({
            'success': True,
            'pay_url': 'alipays://platformapi/startapp?appId=20000067&actionType=toAccount&goBack=YES',
            'qr_code': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==',
            'payment_id': payment.id
        })

    @action(detail=True, methods=['get'])
    def card_pay(self, request, pk=None):
        """银行卡支付模拟"""
        payment = self.get_object()
        
        # 模拟银行卡支付接口返回
        return Response({
            'success': True,
            'pay_url': '/api/mall/payments/{}/card-form'.format(pk),
            'payment_id': payment.id
        })

    @action(detail=True, methods=['post'])
    def notify(self, request, pk=None):
        """支付回调处理"""
        payment = self.get_object()
        
        # 模拟支付回调
        payment.status = 'success'
        payment.transaction_id = f"TRX{int(timezone.now().timestamp())}{uuid.uuid4().hex[:8].upper()}"
        payment.paid_at = timezone.now()
        payment.save()

        # 更新订单状态
        order = payment.order
        order.status = 'paid'
        order.paid_at = timezone.now()
        order.payment_method = payment.method
        order.save()

        return Response({'success': True, 'message': '支付成功'})

    @action(detail=True, methods=['get'])
    def query(self, request, pk=None):
        """查询支付状态"""
        payment = self.get_object()
        
        return Response({
            'payment_id': payment.id,
            'status': payment.status,
            'amount': payment.amount,
            'method': payment.method,
            'created_at': payment.created_at,
            'paid_at': payment.paid_at
        })


class FlashSaleViewSet(viewsets.ModelViewSet):
    """秒杀活动视图集"""
    queryset = FlashSale.objects.all()
    serializer_class = FlashSaleSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def current(self, request):
        """获取当前正在进行的秒杀活动"""
        now = timezone.now()
        current_sales = self.queryset.filter(
            status=True,
            start_time__lte=now,
            end_time__gte=now
        )
        serializer = self.get_serializer(current_sales, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def purchase(self, request, pk=None):
        """秒杀购买"""
        flash_sale = self.get_object()
        serializer = FlashSalePurchaseSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            data = serializer.validated_data
            product_id = data['product_id']
            quantity = data['quantity']

            try:
                with transaction.atomic():
                    # 检查秒杀商品
                    flash_product = FlashSaleProduct.objects.select_for_update().get(
                        flash_sale=flash_sale,
                        product_id=product_id
                    )

                    # 检查库存
                    if flash_product.flash_stock < quantity:
                        return Response({'error': '秒杀库存不足'}, status=status.HTTP_400_BAD_REQUEST)

                    # 检查限购
                    purchase_count, created = UserCoupon.objects.get_or_create(
                        user=request.user,
                        coupon=flash_product,
                        defaults={'purchased_count': quantity}
                    )
                    if not created:
                        if purchase_count.purchased_count + quantity > flash_product.limit_per_user:
                            return Response({'error': '超过限购数量'}, status=status.HTTP_400_BAD_REQUEST)
                        purchase_count.purchased_count += quantity
                        purchase_count.save()

                    # 扣减库存
                    flash_product.flash_stock -= quantity
                    flash_product.save()

                    # 跳转到结算页面
                    return Response({'success': True, 'product_id': product_id})
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CouponViewSet(viewsets.ModelViewSet):
    """优惠券视图集"""
    queryset = Coupon.objects.filter(is_active=True)
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def available(self, request):
        """获取可领取的优惠券"""
        now = timezone.now()
        available_coupons = self.queryset.filter(
            start_time__lte=now,
            end_time__gte=now,
            remaining_quantity__gt=0
        )
        serializer = self.get_serializer(available_coupons, many=True)
        return Response(serializer.data)


class UserCouponViewSet(viewsets.ModelViewSet):
    """用户优惠券视图集"""
    queryset = UserCoupon.objects.all()
    serializer_class = UserCouponSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """获取当前用户的优惠券"""
        return self.queryset.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def apply(self, request):
        """领取优惠券"""
        serializer = CouponApplySerializer(data=request.data)
        if serializer.is_valid():
            coupon_id = serializer.validated_data['coupon_id']
            coupon = Coupon.objects.get(id=coupon_id)

            try:
                with transaction.atomic():
                    # 检查是否已经领取
                    if UserCoupon.objects.filter(user=request.user, coupon=coupon).exists():
                        return Response({'error': '已经领取过该优惠券'}, status=status.HTTP_400_BAD_REQUEST)

                    # 扣减优惠券库存
                    if coupon.remaining_quantity <= 0:
                        return Response({'error': '优惠券已领完'}, status=status.HTTP_400_BAD_REQUEST)
                    coupon.remaining_quantity -= 1
                    coupon.save()

                    # 创建用户优惠券
                    user_coupon = UserCoupon.objects.create(
                        user=request.user,
                        coupon=coupon
                    )

                    return Response({'success': True, 'coupon_id': user_coupon.id})
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogisticsViewSet(viewsets.ModelViewSet):
    """物流视图集"""
    queryset = Logistics.objects.all()
    serializer_class = LogisticsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """获取当前用户的物流信息"""
        return self.queryset.filter(order__user=self.request.user)

    @action(detail=True, methods=['get'])
    def track(self, request, pk=None):
        """查询物流轨迹"""
        logistics = self.get_object()
        if logistics.trajectory:
            try:
                trajectory = json.loads(logistics.trajectory)
                return Response({'trajectory': trajectory})
            except:
                return Response({'trajectory': []})
        return Response({'trajectory': []})

    @action(detail=False, methods=['post'])
    def create_logistics(self, request):
        """创建物流订单"""
        try:
            order_id = request.data.get('order_id')
            logistics_company = request.data.get('logistics_company')
            logistics_no = request.data.get('logistics_no')

            if not order_id or not logistics_company or not logistics_no:
                return Response({'error': '缺少必要参数'}, status=status.HTTP_400_BAD_REQUEST)

            # 验证订单
            order = get_object_or_404(Order, id=order_id, user=request.user)
            if order.status not in ['paid', 'shipped']:
                return Response({'error': '订单状态不允许创建物流'}, status=status.HTTP_400_BAD_REQUEST)

            # 检查是否已存在物流信息
            if hasattr(order, 'logistics'):
                return Response({'error': '订单已存在物流信息'}, status=status.HTTP_400_BAD_REQUEST)

            # 创建物流信息
            logistics = Logistics.objects.create(
                order=order,
                logistics_company=logistics_company,
                logistics_no=logistics_no,
                status='shipped',
                latest_status='【{}】您的订单已发货，请注意查收'.format(logistics_company)
            )

            # 更新订单状态
            order.status = 'shipped'
            order.logistics_company = logistics_company
            order.logistics_no = logistics_no
            order.shipped_at = timezone.now()
            order.save()

            # 生成初始物流轨迹
            trajectory = [
                {
                    'time': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'status': '已发货',
                    'description': '【{}】您的订单已发货，请注意查收'.format(logistics_company)
                }
            ]
            logistics.trajectory = json.dumps(trajectory)
            logistics.save()

            return Response({
                'success': True,
                'logistics_id': logistics.id,
                'logistics_no': logistics_no,
                'order_number': order.order_number
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'])
    def update_status(self, request, pk=None):
        """更新物流状态"""
        logistics = self.get_object()
        
        try:
            new_status = request.data.get('status')
            status_description = request.data.get('status_description')

            if not new_status:
                return Response({'error': '缺少状态参数'}, status=status.HTTP_400_BAD_REQUEST)

            # 验证状态值
            valid_statuses = [choice[0] for choice in Logistics.LOGISTICS_STATUS_CHOICES]
            if new_status not in valid_statuses:
                return Response({'error': '无效的状态值'}, status=status.HTTP_400_BAD_REQUEST)

            # 更新物流状态
            logistics.status = new_status
            if status_description:
                logistics.latest_status = status_description
            logistics.save()

            # 更新订单状态
            order = logistics.order
            if new_status == 'delivered':
                order.status = 'delivered'
                order.delivered_at = timezone.now()
                order.save()

            # 更新物流轨迹
            if logistics.trajectory:
                try:
                    trajectory = json.loads(logistics.trajectory)
                except:
                    trajectory = []
            else:
                trajectory = []

            # 添加新的轨迹记录
            trajectory.append({
                'time': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': dict(Logistics.LOGISTICS_STATUS_CHOICES).get(new_status),
                'description': status_description or dict(Logistics.LOGISTICS_STATUS_CHOICES).get(new_status)
            })

            logistics.trajectory = json.dumps(trajectory)
            logistics.save()

            return Response({
                'success': True,
                'status': new_status,
                'status_description': status_description
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def simulate_trajectory(self, request, pk=None):
        """模拟物流轨迹"""
        logistics = self.get_object()
        
        # 生成模拟物流轨迹
        trajectory = [
            {
                'time': (timezone.now() - timezone.timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
                'status': '已下单',
                'description': '【{}】您的订单已创建，等待支付'.format(logistics.logistics_company)
            },
            {
                'time': (timezone.now() - timezone.timedelta(days=1, hours=12)).strftime('%Y-%m-%d %H:%M:%S'),
                'status': '已支付',
                'description': '【{}】您的订单已支付，等待发货'.format(logistics.logistics_company)
            },
            {
                'time': (timezone.now() - timezone.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
                'status': '已发货',
                'description': '【{}】您的订单已发货，请注意查收'.format(logistics.logistics_company)
            },
            {
                'time': (timezone.now() - timezone.timedelta(hours=12)).strftime('%Y-%m-%d %H:%M:%S'),
                'status': '运输中',
                'description': '【{}】您的包裹正在运输途中'.format(logistics.logistics_company)
            },
            {
                'time': (timezone.now() - timezone.timedelta(hours=6)).strftime('%Y-%m-%d %H:%M:%S'),
                'status': '运输中',
                'description': '【{}】您的包裹已到达【{}】'.format(logistics.logistics_company, '北京转运中心')
            },
            {
                'time': (timezone.now() - timezone.timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
                'status': '派送中',
                'description': '【{}】您的包裹正在派送中，快递员：【张三】，电话：【13800138000】'.format(logistics.logistics_company)
            }
        ]

        # 如果状态是已送达，添加送达记录
        if logistics.status == 'delivered':
            trajectory.append({
                'time': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': '已送达',
                'description': '【{}】您的包裹已送达，感谢您的使用'.format(logistics.logistics_company)
            })

        # 更新物流轨迹
        logistics.trajectory = json.dumps(trajectory)
        logistics.save()

        return Response({'trajectory': trajectory})

    @action(detail=False, methods=['get'])
    def logistics_companies(self, request):
        """获取物流公司列表"""
        companies = [
            {'id': 'SF', 'name': '顺丰速运'},
            {'id': 'YT', 'name': '圆通快递'},
            {'id': 'YD', 'name': '韵达快递'},
            {'id': 'ZT', 'name': '中通快递'},
            {'id': 'ST', 'name': '申通快递'},
            {'id': 'EMS', 'name': 'EMS'},
            {'id': 'JD', 'name': '京东物流'},
            {'id': 'DD', 'name': '达达快递'}
        ]
        return Response({'companies': companies})

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """查询物流状态"""
        logistics = self.get_object()
        
        return Response({
            'logistics_id': logistics.id,
            'logistics_no': logistics.logistics_no,
            'logistics_company': logistics.logistics_company,
            'status': logistics.status,
            'status_text': dict(Logistics.LOGISTICS_STATUS_CHOICES).get(logistics.status),
            'latest_status': logistics.latest_status,
            'order_number': logistics.order.order_number,
            'created_at': logistics.created_at,
            'updated_at': logistics.updated_at
        })


class ProductMarkViewSet(viewsets.ModelViewSet):
    """商品收藏视图集"""
    queryset = ProductMark.objects.all()
    serializer_class = ProductMarkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """获取当前用户的商品收藏"""
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """创建商品收藏"""
        serializer.save(user=self.request.user)


class HomeBannerViewSet(viewsets.ModelViewSet):
    """首页轮播图视图集"""
    queryset = HomeBanner.objects.filter(is_active=True)
    serializer_class = HomeBannerSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def active(self, request):
        """获取当前有效的轮播图"""
        now = timezone.now()
        active_banners = self.queryset.filter(
            start_time__lte=now,
            end_time__gte=now
        ).order_by('sort')
        serializer = self.get_serializer(active_banners, many=True)
        return Response(serializer.data)


class ProductTagViewSet(viewsets.ModelViewSet):
    """商品标签视图集"""
    queryset = ProductTag.objects.filter(is_active=True)
    serializer_class = ProductTagSerializer
    permission_classes = [IsAuthenticated]


class UserBehaviorViewSet(viewsets.ModelViewSet):
    """用户行为视图集"""
    queryset = UserBehavior.objects.all()
    serializer_class = UserBehaviorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """获取当前用户的行为记录"""
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """创建用户行为记录"""
        serializer.save(user=self.request.user)


class RefundApplicationViewSet(viewsets.ModelViewSet):
    """退款申请视图集"""
    queryset = RefundApplication.objects.all()
    serializer_class = RefundApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """获取当前用户的退款申请"""
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """创建退款申请"""
        serializer.save(user=self.request.user)


# Web视图函数

# 推荐商品装饰器
def recommend_view(func):
    def _wrapper(request, *args, **kwargs):
        # 从cookie中获取用户访问的所有商品id
        c_id = request.COOKIES.get('rem', '')

        # 存放用户访问商品的id列表，使用逗号分隔
        visited_ids = [gid for gid in c_id.split(',') if gid.strip()]

        # 构建推荐商品列表
        recommended_products = []
        if visited_ids:
            # 从用户访问过的商品中推荐前5个
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
def mall(request):
    """商城首页"""
    # 获取推荐商品
    recommended_products = getattr(request, 'recommended_products', [])
    if not recommended_products:
        recommended_products = Product.objects.order_by('?')[:5]

    # 获取热卖商品类型参数
    hot_type = request.GET.get('hot_type', '30d')
    valid_hot_types = ['7d', '30d', 'new']
    if hot_type not in valid_hot_types:
        hot_type = '30d'

    # 定义热卖商品描述
    hot_desc_map = {
        '7d': '近7天热卖',
        '30d': '近30天热卖',
        'new': '新品热卖'
    }
    hot_desc = hot_desc_map.get(hot_type, '近30天热卖')

    # 获取缓存过期时间
    HOT_PRODUCTS_CACHE_TTL = int(os.getenv('HOT_PRODUCTS_CACHE_TTL', 3600))
    HOT_PRODUCTS_EMPTY_TTL = int(os.getenv('HOT_PRODUCTS_EMPTY_TTL', 600))

    # 尝试从热卖商品缓存获取数据
    cache_key = f'hot_products:{hot_type}'
    hot_products_data = None

    try:
        from django.core.cache import caches
        hot_products_cache = caches['hot_products']
        hot_products_data = hot_products_cache.get(cache_key)
    except Exception as e:
        print(f"Redis缓存读取失败: {e}")
        # Redis连接失败，降级为数据库查询
        hot_products_data = None

    if hot_products_data:
        # 缓存命中
        hot_products = hot_products_data
    else:
        # 缓存未命中，从数据库查询
        # 计算时间范围
        now = timezone.now()
        if hot_type == '7d':
            start_date = now - timezone.timedelta(days=7)
        elif hot_type == '30d' or hot_type == 'new':
            start_date = now - timezone.timedelta(days=30)
        else:
            start_date = now - timezone.timedelta(days=30)

        # 定义有效订单状态
        valid_order_statuses = ['paid', 'shipped', 'delivered', 'completed']

        # 基础查询集：过滤上架且有库存的商品
        base_products = Product.objects.filter(
            is_active=True,
            product_stock__gt=0
        )

        # 根据hot_type获取商品
        if hot_type == 'new':
            # 新品热卖：近30天上架的商品
            new_products = base_products.filter(
                created_at__gte=start_date
            )
            # 统计销量
            hot_products_queryset = new_products.annotate(
                real_sales=Sum(
                    Case(
                        When(
                            orderitem__order__status__in=valid_order_statuses,
                            then=F('orderitem__quantity')
                        ),
                        default=0,
                        output_field=IntegerField()
                    )
                )
            ).annotate(
                composite_score=Case(
                    When(
                        real_sales__gt=0,
                        then=F('real_sales') * 0.7 + F('rating') * 0.3
                    ),
                    default=0,
                    output_field=FloatField()
                )
            ).order_by('-composite_score')[:6]
        else:
            # 近7天或30天热卖
            hot_products_queryset = base_products.annotate(
                real_sales=Sum(
                    Case(
                        When(
                            orderitem__order__status__in=valid_order_statuses,
                            orderitem__order__created_at__gte=start_date,
                            then=F('orderitem__quantity')
                        ),
                        default=0,
                        output_field=IntegerField()
                    )
                )
            ).annotate(
                composite_score=Case(
                    When(
                        real_sales__gt=0,
                        then=F('real_sales') * 0.7 + F('rating') * 0.3
                    ),
                    default=0,
                    output_field=FloatField()
                )
            ).order_by('-composite_score')[:6]

        # 将查询集转换为字典列表
        hot_products = []
        for i, product in enumerate(hot_products_queryset):
            # 为商品添加rank_tag属性
            if i == 0:
                rank_tag = 'first'
            elif i == 1:
                rank_tag = 'second'
            elif i == 2:
                rank_tag = 'third'
            else:
                rank_tag = 'normal'

            # 构建商品字典
            product_dict = {
                'id': str(product.id),
                'name': product.name,
                'price': float(product.price),
                'rating': product.rating,
                'stock': product.product_stock,
                'is_on_sale': product.is_active,
                'real_sales': product.real_sales if hasattr(product, 'real_sales') else 0,
                'composite_score': product.composite_score if hasattr(product, 'composite_score') else 0,
                'rank_tag': rank_tag,
                'main_image': product.main_image.url if product.main_image else '',
                'created_at': product.created_at.isoformat() if product.created_at else None,
                'is_new': product.is_new,
                'old_price': float(product.old_price)
            }
            hot_products.append(product_dict)
        # 缓存数据到热卖商品缓存
        try:
            from django.core.cache import caches
            hot_products_cache = caches['hot_products']
            if hot_products:
                # 正常数据缓存
                hot_products_cache.set(cache_key, hot_products, HOT_PRODUCTS_CACHE_TTL)
            else:
                # 空数据缓存
                hot_products_cache.set(cache_key, hot_products, HOT_PRODUCTS_EMPTY_TTL)
        except Exception as e:
            print(f"Redis缓存写入失败: {e}")
            # Redis连接失败，忽略缓存写入错误
            pass

    # 获取情侣款商品
    couple_products = Product.objects.filter(is_couple_product=True).order_by('-created_at')[:6]

    # 获取当前秒杀活动
    now = timezone.now()
    # 尝试从缓存获取
    cache_key = f'mall_active:{now.year}:{now.month}:{now.day}:{request.user.is_vip if hasattr(request.user, "is_vip") else "false"}'
    current_flash_sales = None
    
    try:
        from django.core.cache import caches
        cache = caches['mall_cache']
        current_flash_sales = cache.get(cache_key)
    except Exception as e:
        print(f"缓存读取失败: {e}")
    
    if current_flash_sales is None:
        # 构建查询
        query = FlashSale.objects.filter(
            status=True,
            start_time__lte=now,
            end_time__gte=now
        )
        
        # 根据用户VIP状态筛选
        if not hasattr(request.user, "is_vip") or not request.user.is_vip:
            query = query.filter(is_vip_only=False)
        
        current_flash_sales = query[:3]
        
        # 缓存结果
        try:
            from django.core.cache import caches
            cache = caches['mall_cache']
            cache.set(cache_key, current_flash_sales, 3600)  # 缓存1小时
        except Exception as e:
            print(f"缓存写入失败: {e}")

    # 获取首页轮播图
    banners = HomeBanner.objects.filter(is_active=True).order_by('sort')[:5]

    # 获取商品分类（顶级分类及其子分类）
    top_categories = Category.objects.filter(is_active=True, parent__isnull=True).order_by('sort')[:8]
    # 为每个顶级分类获取子分类
    categories_with_children = []
    for category in top_categories:
        category_dict = {
            'id': category.id,
            'name': category.name,
            'icon': category.icon.url if category.icon else '',
            'children': [
                {
                    'id': child.id,
                    'name': child.name
                }
                for child in category.children.filter(is_active=True).order_by('sort')[:5]
            ]
        }
        categories_with_children.append(category_dict)
    
    # 获取用户收藏的商品
    user_marks = ProductMark.objects.filter(user=request.user).values_list('product_id', flat=True)

    return render(request, 'mall/mall.html', {
        'recommended_products': recommended_products,
        'hot_products': hot_products,
        'hot_type': hot_type,
        'hot_desc': hot_desc,
        'couple_products': couple_products,
        'current_flash_sales': current_flash_sales,
        'banners': banners,
        'categories': categories_with_children,
        'user': request.user,
        'user_marks': user_marks
    })


# 商品详情页面
@login_required
@recommend_view
def product_detail(request, product_id):
    """商品详情页面"""
    product = get_object_or_404(Product, id=product_id)

    # 记录用户浏览行为
    UserBehavior.objects.create(
        user=request.user,
        product=product,
        behavior_type='view'
    )

    # 获取推荐商品
    recommended_products = getattr(request, 'recommended_products', [])
    if not recommended_products:
        recommended_products = Product.objects.order_by('-rating')[:5]

    # 获取相关商品
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product_id)[:4]

    # 获取商品规格
    skus = ProductSKU.objects.filter(product=product, is_active=True)

    # 检查是否已收藏
    is_marked = ProductMark.objects.filter(user=request.user, product=product).exists()

    # 获取商品评论
    reviews = ProductReview.objects.filter(product=product, is_approved=True).order_by('-created_at')[:10]

    # 计算平均评分
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    return render(request, 'mall/product_detail.html', {
        'product': product,
        'recommended_products': recommended_products,
        'related_products': related_products,
        'skus': skus,
        'is_marked': is_marked,
        'reviews': reviews,
        'average_rating': average_rating
    })


# 添加商品到购物车
@login_required
@require_POST
def add_to_cart(request):
    """添加商品到购物车"""
    try:
        # 获取请求参数
        product_id = request.POST.get('product_id')
        sku_id = request.POST.get('sku_id')
        quantity = int(request.POST.get('quantity', 1))

        # 验证参数
        if not product_id or quantity <= 0:
            return JsonResponse({'status': 'error', 'message': '无效的商品ID或数量'})

        # 获取商品
        product = get_object_or_404(Product, id=product_id)

        # 获取SKU（如果有）
        sku = None
        if sku_id:
            sku = get_object_or_404(ProductSKU, id=sku_id, product=product)
            # 检查SKU库存
            if sku.stock < quantity:
                return JsonResponse({'status': 'error', 'message': '库存不足'})
        else:
            # 检查商品库存
            if product.product_stock < quantity:
                return JsonResponse({'status': 'error', 'message': '库存不足'})

        # 创建或更新购物车项
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            sku=sku,
            defaults={'quantity': quantity}
        )

        if not created:
            # 更新数量
            cart_item.quantity += quantity
            cart_item.save()

        # 记录用户行为
        UserBehavior.objects.create(
            user=request.user,
            product=product,
            behavior_type='add_cart'
        )

        # 更新缓存
        user_id = request.user.id
        cart_key = f'user_cart:{user_id}'
        try:
            from django.core.cache import caches
            mall_cache = caches['mall_cache']
            mall_cache.delete(cart_key)
        except Exception as e:
            print(f"Redis缓存操作失败: {e}")
            cache.delete(cart_key)

        return JsonResponse({'status': 'success', 'message': '已添加到购物车'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


# 购物车页面
@login_required
def mallcart(request):
    """购物车页面"""
    # 获取用户购物车项
    cart_items = CartItem.objects.filter(user=request.user).select_related('product', 'sku')

    # 计算总价
    total_price = 0
    selected_count = 0
    for item in cart_items:
        if item.selected:
            item_total = item.total_price
            total_price += item_total
            selected_count += 1

    # 将购物车项转换为可序列化的字典列表
    cart_items_data = []
    for item in cart_items:
        cart_item_data = {
            'id': item.id,
            'product_id': item.product.id,
            'product_name': item.product.name,
            'price': float(item.total_price / item.quantity),  # 单价
            'quantity': item.quantity,
            'selected': item.selected,
            'style': item.sku.name if item.sku else '默认',
            'total_price': float(item.total_price)
        }
        # 添加商品图片
        if item.sku and item.sku.image:
            cart_item_data['image'] = item.sku.image.url
        elif item.product.main_image:
            cart_item_data['image'] = item.product.main_image.url
        else:
            cart_item_data['image'] = ''
        cart_items_data.append(cart_item_data)

    # 获取推荐商品
    # 从cookie中获取用户访问的商品id
    c_id = request.COOKIES.get('rem', '')
    visited_ids = [gid for gid in c_id.split(',') if gid.strip()]
    
    recommended_products = []
    if visited_ids:
        # 从用户访问过的商品中推荐
        recommended_products = Product.objects.filter(id__in=visited_ids[:5])
    
    # 如果没有推荐商品，随机获取一些
    if not recommended_products:
        recommended_products = Product.objects.order_by('?')[:4]

    return render(request, 'mall/mallcart.html', {
        'cart_items': cart_items,
        'cart_items_data': cart_items_data,
        'total_price': total_price,
        'selected_count': selected_count,
        'recommended_products': recommended_products
    })


# 更新购物车
@login_required
@require_POST
def update_cart(request):
    """更新购物车"""
    try:
        data = json.loads(request.body)
        user = request.user

        # 获取所有键作为字符串类型的购物车项ID
        item_ids = list(data.keys())

        # 删除数据库中存在但不在前端数据中的购物车项（即用户删除的商品）
        user_cart_items = CartItem.objects.filter(user=user)
        for cart_item in user_cart_items:
            if str(cart_item.id) not in item_ids:
                cart_item.delete()

        # 更新前端发送的购物车项
        for item_id, item_data in data.items():
            try:
                cart_item = CartItem.objects.get(id=item_id, user=user)
                # 更新数量
                if 'quantity' in item_data:
                    cart_item.quantity = item_data['quantity']
                # 更新选中状态
                if 'selected' in item_data:
                    cart_item.selected = item_data['selected']
                cart_item.save()
            except CartItem.DoesNotExist:
                pass

        # 清除缓存
        cart_key = f'user_cart:{user.id}'
        try:
            from django.core.cache import caches
            mall_cache = caches['mall_cache']
            mall_cache.delete(cart_key)
        except Exception as e:
            print(f"Redis缓存操作失败: {e}")
            cache.delete(cart_key)

        return JsonResponse({'status': 'success', 'message': '购物车已更新'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


# 删除购物车项
@login_required
@require_POST
def delete_cart_item(request):
    """删除购物车项"""
    try:
        item_id = request.POST.get('item_id')
        cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
        cart_item.delete()

        # 清除缓存
        cart_key = f'user_cart:{request.user.id}'
        try:
            from django.core.cache import caches
            mall_cache = caches['mall_cache']
            mall_cache.delete(cart_key)
        except Exception as e:
            print(f"Redis缓存操作失败: {e}")
            cache.delete(cart_key)

        return JsonResponse({'status': 'success', 'message': '已删除'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


# 刷新推荐商品
@login_required
def refresh_recommended(request):
    """刷新推荐商品"""
    try:
        # 随机获取5个商品作为新的推荐
        recommended_products = Product.objects.filter(is_active=True).order_by('?')[:5]

        # 获取用户收藏的商品
        user_marks = ProductMark.objects.filter(user=request.user).values_list('product_id', flat=True)

        # 构建商品数据
        products_data = []
        for product in recommended_products:
            products_data.append({
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'rating': product.rating,
                'main_image': product.main_image.url if product.main_image else None,
                'is_marked': product.id in user_marks,
                'is_new': product.is_new
            })

        return JsonResponse({
            'success': True,
            'products': products_data
        })
    except Exception as e:
        print(f"刷新推荐商品失败: {e}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


# 清除活动缓存的函数
def clear_flash_sale_cache():
    """清除活动缓存"""
    try:
        from django.core.cache import caches
        from datetime import datetime
        cache = caches['mall_cache']
        # 清除当前日期的活动缓存
        now = datetime.now()
        # 清除不同类型活动的缓存，统一在mall_active键名下
        cache_keys = [
            # 首页活动列表缓存
            f'mall_active:{now.year}:{now.month}:{now.day}:false',
            f'mall_active:{now.year}:{now.month}:{now.day}:true',
            # 活动详情页缓存
            f'mall_active:flash:{now.year}:{now.month}:{now.day}:false',
            f'mall_active:flash:{now.year}:{now.month}:{now.day}:true',
            f'mall_active:new:{now.year}:{now.month}:{now.day}:false',
            f'mall_active:new:{now.year}:{now.month}:{now.day}:true',
            f'mall_active:vip:{now.year}:{now.month}:{now.day}:false',
            f'mall_active:vip:{now.year}:{now.month}:{now.day}:true'
        ]
        for cache_key in cache_keys:
            cache.delete(cache_key)
            print(f"已清除活动缓存: {cache_key}")
    except Exception as e:
        print(f"清除活动缓存失败: {e}")

# 分类商品页面
@login_required
def category_products(request, category_id):
    """分类商品页面"""
    # 获取分类
    category = get_object_or_404(Category, id=category_id, is_active=True)
    
    # 获取分类下的商品
    products_queryset = Product.objects.filter(
        is_active=True,
        category=category,
        product_stock__gt=0
    ).order_by('-created_at')[:20]
    
    # 为商品添加discount属性
    products = []
    for product in products_queryset:
        if product.old_price > product.price:
            product.discount = int((1 - product.price / product.old_price) * 100)
        else:
            product.discount = 0
        products.append(product)
    
    # 获取推荐商品
    recommended_queryset = Product.objects.filter(
        is_active=True,
        product_stock__gt=0
    ).exclude(category=category).order_by('?')[:5]
    
    # 为推荐商品添加discount属性
    recommended_products = []
    for product in recommended_queryset:
        if product.old_price > product.price:
            product.discount = int((1 - product.price / product.old_price) * 100)
        else:
            product.discount = 0
        recommended_products.append(product)
    
    # 获取用户收藏的商品
    user_marks = ProductMark.objects.filter(user=request.user).values_list('product_id', flat=True)
    
    return render(request, 'mall/category_products.html', {
        'category': category,
        'products': products,
        'recommended_products': recommended_products,
        'user_marks': user_marks,
        'user': request.user
    })


# 新品商品页面
@login_required
def new_products(request):
    """新品商品页面"""
    # 获取新品商品
    now = timezone.now()
    # 尝试从缓存获取
    cache_key = f'mall_active:new:{now.year}:{now.month}:{now.day}:{request.user.is_vip if hasattr(request.user, "is_vip") else "false"}'
    products = None
    recommended_products = None
    user_marks = None
    
    try:
        from django.core.cache import caches
        cache = caches['mall_cache']
        cached_data = cache.get(cache_key)
        if cached_data:
            products = cached_data['products']
            recommended_products = cached_data['recommended']
            user_marks = cached_data['user_marks']
    except Exception as e:
        print(f"缓存读取失败: {e}")
    
    if products is None or recommended_products is None:
        products_queryset = Product.objects.filter(
            is_active=True,
            is_new=True,
            product_stock__gt=0
        ).order_by('-created_at')[:20]
        
        # 为商品添加discount属性（新品不显示折扣）
        products = []
        for product in products_queryset:
            # 新品不显示折扣
            product.discount = 0
            products.append(product)
        
        # 获取推荐商品
        recommended_queryset = Product.objects.filter(
            is_active=True,
            product_stock__gt=0
        ).exclude(is_new=True).order_by('?')[:5]
        
        # 为推荐商品添加discount属性
        recommended_products = []
        for product in recommended_queryset:
            if product.old_price > product.price:
                product.discount = int((1 - product.price / product.old_price) * 100)
            else:
                product.discount = 0
            recommended_products.append(product)
        
        # 获取用户收藏的商品
        user_marks = ProductMark.objects.filter(user=request.user).values_list('product_id', flat=True)
        
        # 缓存结果
        try:
            from django.core.cache import caches
            cache = caches['mall_cache']
            cache.set(cache_key, {
                'products': products,
                'recommended': recommended_products,
                'user_marks': user_marks
            }, 3600)  # 缓存1小时
        except Exception as e:
            print(f"缓存写入失败: {e}")
    
    # 创建一个虚拟的分类对象用于模板显示
    class VirtualCategory:
        def __init__(self):
            self.id = 0
            self.name = "新品上市"
            self.icon = None
    
    virtual_category = VirtualCategory()
    
    return render(request, 'mall/category_products.html', {
        'category': virtual_category,
        'products': products,
        'recommended_products': recommended_products,
        'user_marks': user_marks,
        'user': request.user
    })


# VIP专属活动页面
@login_required
def vip_products(request):
    """VIP专属活动页面"""
    now = timezone.now()
    # 尝试从缓存获取
    cache_key = f'mall_active:vip:{now.year}:{now.month}:{now.day}:{request.user.is_vip if hasattr(request.user, "is_vip") else "false"}'
    products = None
    recommended_products = None
    user_marks = None
    vip_activity = None
    
    try:
        from django.core.cache import caches
        cache = caches['mall_cache']
        cached_data = cache.get(cache_key)
        if cached_data:
            products = cached_data['products']
            recommended_products = cached_data['recommended']
            user_marks = cached_data['user_marks']
            vip_activity = cached_data['activity']
    except Exception as e:
        print(f"缓存读取失败: {e}")
    
    if products is None or recommended_products is None:
        try:
            # 获取ID为3的活动（VIP专属活动）
            vip_activity = FlashSale.objects.get(id=3, status=True)
            
            # 获取活动关联的商品
            flash_sale_product_ids = FlashSaleProduct.objects.filter(
                flash_sale=vip_activity
            ).values_list('product_id', flat=True)
            
            # 获取商品详情
            products_queryset = Product.objects.filter(
                id__in=flash_sale_product_ids,
                is_active=True,
                product_stock__gt=0
            ).order_by('-created_at')[:20]
            
            # 为商品添加discount属性
            products = []
            for product in products_queryset:
                if product.old_price > product.price:
                    product.discount = int((1 - product.price / product.old_price) * 100)
                else:
                    product.discount = 0
                products.append(product)
            
            # 获取推荐商品
            recommended_queryset = Product.objects.filter(
                is_active=True,
                product_stock__gt=0
            ).exclude(id__in=[p.id for p in products]).order_by('?')[:5]
            
            # 为推荐商品添加discount属性
            recommended_products = []
            for product in recommended_queryset:
                if product.old_price > product.price:
                    product.discount = int((1 - product.price / product.old_price) * 100)
                else:
                    product.discount = 0
                recommended_products.append(product)
            
            # 获取用户收藏的商品
            user_marks = ProductMark.objects.filter(user=request.user).values_list('product_id', flat=True)
            
            # 缓存结果
            try:
                from django.core.cache import caches
                cache = caches['mall_cache']
                cache.set(cache_key, {
                    'products': products,
                    'recommended': recommended_products,
                    'user_marks': user_marks,
                    'activity': vip_activity
                }, 3600)  # 缓存1小时
            except Exception as e:
                print(f"缓存写入失败: {e}")
        except FlashSale.DoesNotExist:
            # 如果活动不存在，显示空页面
            products = []
            recommended_products = []
            user_marks = []
            vip_activity = None
    
    # 创建一个虚拟的分类对象用于模板显示
    class VirtualCategory:
        def __init__(self, name):
            self.id = 0
            self.name = name
            self.icon = None
    
    if vip_activity:
        virtual_category = VirtualCategory(vip_activity.name)
    else:
        class VirtualCategory:
            def __init__(self):
                self.id = 0
                self.name = "VIP专属"
                self.icon = None
        
        virtual_category = VirtualCategory()
    
    return render(request, 'mall/category_products.html', {
        'category': virtual_category,
        'products': products,
        'recommended_products': recommended_products,
        'user_marks': user_marks,
        'user': request.user
    })






# 结算页面
@login_required
def checkout(request):
    """结算页面"""
    # 检查是否是直接购买
    direct_purchase = request.GET.get('direct_purchase') == 'true'
    product_id = request.GET.get('product_id')
    quantity = request.GET.get('quantity', 1)

    # 如果是直接购买
    if direct_purchase and product_id:
        try:
            # 获取商品信息
            product = get_object_or_404(Product, id=product_id)
            # 创建一个临时的购物车项对象，用于在模板中显示
            class TempCartItem:
                def __init__(self, product, quantity):
                    self.product = product
                    self.quantity = int(quantity)
                    self.price = product.price
                    self.total_price = product.price * int(quantity)
                    self.sku = None

            # 创建临时的购物车项
            temp_item = TempCartItem(product, quantity)
            selected_items = [temp_item]

            # 计算商品总价
            goods_total = temp_item.total_price

            # 计算运费
            shipping_fee = 0 if goods_total >= 99 else 10

            # 计算订单总价
            order_total = goods_total + shipping_fee
        except Exception as e:
            # 如果出现错误，重定向到购物车页面
            return redirect('mall:mallcart')
    else:
        # 否则，获取选中的购物车项
        selected_items = CartItem.objects.filter(user=request.user, selected=True).select_related('product', 'sku')

        if not selected_items:
            return redirect('mall:mallcart')

        # 计算商品总价
        goods_total = 0
        for item in selected_items:
            goods_total += item.total_price

        # 计算运费
        shipping_fee = 0 if goods_total >= 99 else 10

        # 计算订单总价
        order_total = goods_total + shipping_fee

    # 获取用户地址
    addresses = Address.objects.filter(user=request.user)
    default_address = addresses.filter(is_default=True).first()

    # 获取可用优惠券
    now = timezone.now()
    available_coupons = UserCoupon.objects.filter(
        user=request.user,
        is_used=False,
        coupon__end_time__gte=now
    )

    # 计算真正可用的优惠券数量（满足最低消费条件）
    truly_available_count = 0
    for user_coupon in available_coupons:
        if user_coupon.coupon.min_spend <= order_total:
            truly_available_count += 1

    return render(request, 'mall/checkout.html', {
        'selected_items': selected_items,
        'goods_total': goods_total,
        'shipping_fee': shipping_fee,
        'order_total': order_total,
        'addresses': addresses,
        'default_address': default_address,
        'available_coupons': available_coupons,
        'truly_available_count': truly_available_count,
        'direct_purchase': direct_purchase,
        'product_id': product_id,
        'quantity': quantity
    })


# 提交订单
@login_required
@require_POST
def submit_order(request):
    """提交订单"""
    try:
        # 获取订单信息
        address_id = request.POST.get('address_id')
        coupon_id = request.POST.get('coupon_id')
        payment_method = request.POST.get('payment_method')

        # 验证地址
        address = get_object_or_404(Address, id=address_id, user=request.user)

        # 获取选中的购物车项
        selected_items = CartItem.objects.filter(user=request.user, selected=True).select_related('product', 'sku')

        if not selected_items:
            return JsonResponse({'status': 'error', 'message': '请选择商品'})

        # 计算订单金额
        goods_total = 0
        order_items_data = []

        # 先计算商品总价
        for item in selected_items:
            price = item.sku.price if item.sku else item.product.price
            item_total = price * item.quantity
            goods_total += item_total
            order_items_data.append({
                'item': item,
                'price': price,
                'item_total': item_total
            })

        # 计算运费和订单总价
        shipping_fee = 0 if goods_total >= 99 else 10
        order_total = goods_total + shipping_fee

        # 应用优惠券
        discount_amount = 0
        used_coupon = None
        
        if coupon_id:
            try:
                user_coupon = UserCoupon.objects.select_related('coupon').get(
                    id=coupon_id, 
                    user=request.user, 
                    is_used=False
                )
                coupon = user_coupon.coupon
                
                # 验证优惠券有效期
                if timezone.now() > coupon.end_time:
                    return JsonResponse({'status': 'error', 'message': '优惠券已过期'})
                
                # 验证使用条件
                if coupon.min_spend > 0 and order_total < coupon.min_spend:
                    return JsonResponse({'status': 'error', 'message': f'订单金额未达到优惠券使用条件（满{coupon.min_spend}元）'})
                
                # 计算优惠金额
                if coupon.type == '满减券':
                    discount_amount = coupon.value
                    order_total -= discount_amount
                elif coupon.type == '折扣券':
                    discount_amount = order_total * (1 - coupon.value / 10)
                    order_total *= (coupon.value / 10)
                elif coupon.type == '现金券':
                    discount_amount = coupon.value
                    order_total -= discount_amount
                else:
                    return JsonResponse({'status': 'error', 'message': '优惠券类型错误'})
                
                # 确保订单金额不小于0
                if order_total < 0:
                    discount_amount += order_total
                    order_total = 0
                
                used_coupon = user_coupon
            except UserCoupon.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': '优惠券不存在或已使用'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': f'优惠券使用失败: {str(e)}'})

        with transaction.atomic():
            # 创建订单
            order = Order.objects.create(
                user=request.user,
                address=address,
                payment_method=payment_method,
                total_amount=max(0, order_total),
                shipping_fee=shipping_fee
            )

            # 创建支付记录
            payment = Payment.objects.create(
                order=order,
                amount=max(0, order_total),
                method=payment_method,
                status='pending'
            )

            # 处理订单商品
            for item_data in order_items_data:
                item = item_data['item']
                price = item_data['price']
                item_total = item_data['item_total']

                # 创建订单项
                order_item = OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    sku=item.sku,
                    quantity=item.quantity,
                    price=price,
                    total_price=item_total
                )

                # 扣减库存
                if item.sku:
                    item.sku.stock -= item.quantity
                    item.sku.save()
                else:
                    item.product.product_stock -= item.quantity
                    item.product.save()

                # 记录用户购买行为
                UserBehavior.objects.create(
                    user=request.user,
                    product=item.product,
                    behavior_type='purchase'
                )

            # 更新优惠券状态
            if used_coupon:
                used_coupon.is_used = True
                used_coupon.used_at = timezone.now()
                used_coupon.used_order = order
                used_coupon.save()
                
                # 记录优惠券使用日志
                try:
                    from django.db import connection
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "INSERT INTO coupon_usage_log (user_id, coupon_id, order_id, discount_amount, created_at) "
                            "VALUES (%s, %s, %s, %s, %s)",
                            [request.user.id, used_coupon.coupon.id, order.id, discount_amount, timezone.now()]
                        )
                except Exception:
                    # 日志记录失败不影响订单提交
                    pass

            # 清空购物车中已下单的商品
            selected_items.delete()

            # 清除缓存
            cart_key = f'user_cart:{request.user.id}'
            try:
                from django.core.cache import caches
                mall_cache = caches['mall_cache']
                mall_cache.delete(cart_key)
            except Exception as e:
                print(f"Redis缓存操作失败: {e}")
                cache.delete(cart_key)

            # 跳转到支付页面
            return JsonResponse({'status': 'success', 'order_id': order.id, 'order_number': order.order_number})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


# 订单列表页面
@login_required
def order_list(request):
    """订单列表页面"""
    # 获取订单状态
    status = request.GET.get('status', 'all')

    # 获取订单
    orders = Order.objects.filter(user=request.user)

    # 按状态筛选
    if status != 'all':
        orders = orders.filter(status=status)

    # 排序
    orders = orders.order_by('-created_at')

    return render(request, 'mall/order_list.html', {
        'orders': orders,
        'status': status
    })


# 订单详情页面
@login_required
def order_detail(request, order_number):
    """订单详情页面"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    # 获取物流信息
    logistics = None
    try:
        logistics = Logistics.objects.get(order=order)
    except Logistics.DoesNotExist:
        pass
    
    # 根据物流状态更新订单状态
    if logistics:
        if logistics.status == 'shipped' and order.status == 'paid':
            order.status = 'shipped'
            order.save()
        elif logistics.status == 'delivered' and order.status == 'shipped':
            order.status = 'delivered'
            order.save()

    return render(request, 'mall/order_detail.html', {
        'order': order,
        'logistics': logistics
    })


# 收藏页面
@login_required
def mallmark(request):
    """商品收藏页面"""
    # 获取排序和筛选参数
    sort_by = request.GET.get('sort', 'created_at')
    filter_by = request.GET.get('filter', 'all')
    
    # 构建查询集
    marks = ProductMark.objects.filter(user=request.user).select_related('product')
    
    # 应用筛选
    if filter_by == 'unavailable':
        marks = marks.filter(product__is_active=False)
    elif filter_by == 'price_drop':
        # 实现降价提醒的逻辑
        # 筛选出价格下降的商品（当前价格低于原价）
        # 首先筛选出有原价记录的商品
        # 然后筛选出当前价格低于原价的商品
        # 正确使用 F 表达式语法
        # 使用双下划线来引用关联模型的字段
        marks = marks.filter(
            product__old_price__gt=0,  # 确保有原价记录
            product__price__lt=F('product__old_price')  # 当前价格低于原价
        )
    elif filter_by == 'all':
        # 显示所有收藏
        pass
    # 默认显示所有收藏
    
    # 应用排序
    if sort_by == 'created_at':
        marks = marks.order_by('-created_at')
    elif sort_by == 'price_asc':
        marks = marks.order_by('product__price')
    elif sort_by == 'price_desc':
        marks = marks.order_by('-product__price')
    elif sort_by == 'newest':
        marks = marks.order_by('-product__created_at')
    else:
        marks = marks.order_by('-created_at')
    
    # 获取推荐商品
    recommended_products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]

    return render(request, 'mall/mallmark.html', {
        'marks': marks,
        'recommended_products': recommended_products,
        'current_sort': sort_by,
        'current_filter': filter_by
    })


# 获取购物车数量
@login_required
def cart_count(request):
    """获取购物车数量"""
    try:
        # 从缓存获取
        user_id = request.user.id
        cart_key = f'user_cart:{user_id}'
        count = None
        
        # 尝试使用商城缓存
        try:
            from django.core.cache import caches
            mall_cache = caches['mall_cache']
            count = mall_cache.get(cart_key)
        except Exception as e:
            print(f"Redis缓存读取失败: {e}")
            count = cache.get(cart_key)
        
        if count is None:
            # 从数据库获取
            count = CartItem.objects.filter(user=request.user).count()
            # 缓存结果，有效期5分钟
            try:
                from django.core.cache import caches
                mall_cache = caches['mall_cache']
                mall_cache.set(cart_key, count, 300)
            except Exception as e:
                print(f"Redis缓存写入失败: {e}")
                cache.set(cart_key, count, 300)
        
        return JsonResponse({'status': 'success', 'count': count})
    except Exception as e:
        return JsonResponse({'status': 'error', 'count': 0, 'message': str(e)})

# 获取收藏数量
@login_required
def mark_count(request):
    """获取收藏数量"""
    try:
        # 从缓存获取
        user_id = request.user.id
        mark_key = f'user_mark:{user_id}'
        count = None
        
        # 尝试使用商城缓存
        try:
            from django.core.cache import caches
            mall_cache = caches['mall_cache']
            count = mall_cache.get(mark_key)
        except Exception as e:
            print(f"Redis缓存读取失败: {e}")
            count = cache.get(mark_key)
        
        if count is None:
            # 从数据库获取
            count = ProductMark.objects.filter(user=request.user).count()
            # 缓存结果，有效期5分钟
            try:
                from django.core.cache import caches
                mall_cache = caches['mall_cache']
                mall_cache.set(mark_key, count, 300)
            except Exception as e:
                print(f"Redis缓存写入失败: {e}")
                cache.set(mark_key, count, 300)
        
        return JsonResponse({'status': 'success', 'count': count})
    except Exception as e:
        return JsonResponse({'status': 'error', 'count': 0, 'message': str(e)})


# 订单评价页面
@login_required
def order_review(request, order_id):
    """订单评价页面"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # 检查订单状态是否允许评价
    if order.status != 'delivered':
        return redirect('mall:order_detail', order_number=order.order_number)
    
    # 获取订单商品
    order_items = order.items.all()
    
    if request.method == 'POST':
        # 处理评价提交
        for item in order_items:
            rating = request.POST.get(f'rating_{item.id}')
            comment = request.POST.get(f'comment_{item.id}')
            images = request.POST.get(f'images_{item.id}', '')
            is_anonymous = request.POST.get(f'anonymous_{item.id}', 'false') == 'true'
            
            if rating and comment:
                # 保存评价
                ProductReview.objects.create(
                    user=request.user,
                    product=item.product,
                    order_item=item,
                    rating=rating,
                    comment=comment,
                    images=images,
                    is_anonymous=is_anonymous
                )
        
        return redirect('mall:order_detail', order_number=order.order_number)
    
    return render(request, 'mall/order_review.html', {
        'order': order,
        'order_items': order_items
    })

# 获取优惠券详情
@login_required
def get_coupon_detail(request, coupon_id):
    """获取优惠券详情"""
    try:
        user_coupon = UserCoupon.objects.select_related('coupon').get(
            id=coupon_id,
            user=request.user,
            is_used=False
        )
        coupon = user_coupon.coupon
        
        # 验证优惠券是否在有效期内
        if timezone.now() > coupon.end_time:
            return JsonResponse({'status': 'error', 'message': '优惠券已过期'})
        
        return JsonResponse({
            'status': 'success',
            'data': {
                'id': user_coupon.id,
                'coupon_id': coupon.id,
                'name': coupon.name,
                'type': coupon.type,
                'value': float(coupon.value),
                'min_spend': float(coupon.min_spend),
                'end_time': coupon.end_time.strftime('%Y-%m-%d'),
                'is_valid': timezone.now() <= coupon.end_time
            }
        })
    except UserCoupon.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '优惠券不存在或已使用'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

# 添加收藏
@login_required
@require_POST
def add_mark(request):
    """添加收藏"""
    try:
        # 尝试从JSON数据中获取商品ID
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            product_id = data.get('product_id')
        else:
            # 从表单数据中获取商品ID
            product_id = request.POST.get('product_id')
        
        if not product_id:
            return JsonResponse({'status': 'error', 'message': '商品ID不能为空'})
            
        product = get_object_or_404(Product, id=product_id)

        # 检查是否已收藏
        mark, created = ProductMark.objects.get_or_create(
            user=request.user,
            product=product
        )

        if created:
            # 记录用户收藏行为
            UserBehavior.objects.create(
                user=request.user,
                product=product,
                behavior_type='mark'
            )
            # 清除缓存
            user_id = request.user.id
            mark_key = f'user_mark:{user_id}'
            try:
                from django.core.cache import caches
                mall_cache = caches['mall_cache']
                mall_cache.delete(mark_key)
            except Exception as e:
                print(f"Redis缓存操作失败: {e}")
                cache.delete(mark_key)
            return JsonResponse({'status': 'success', 'message': '收藏成功'})
        else:
            return JsonResponse({'status': 'info', 'message': '已收藏'})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'JSON数据解析失败'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


# 取消收藏
@login_required
@require_POST
def remove_mark(request):
    """取消收藏"""
    try:
        # 尝试从JSON数据中获取商品ID
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            product_id = data.get('product_id')
        else:
            # 从表单数据中获取商品ID
            product_id = request.POST.get('product_id')
        
        if not product_id:
            return JsonResponse({'status': 'error', 'message': '商品ID不能为空'})
            
        product = get_object_or_404(Product, id=product_id)

        mark = get_object_or_404(ProductMark, user=request.user, product=product)
        mark.delete()

        # 清除缓存
        user_id = request.user.id
        mark_key = f'user_mark:{user_id}'
        try:
            from django.core.cache import caches
            mall_cache = caches['mall_cache']
            mall_cache.delete(mark_key)
        except Exception as e:
            print(f"Redis缓存操作失败: {e}")
            cache.delete(mark_key)

        return JsonResponse({'status': 'success', 'message': '已取消收藏'})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'JSON数据解析失败'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


# 秒杀活动页面
@login_required
def flash_sale(request):
    """秒杀活动页面"""
    # 获取当前秒杀活动
    now = timezone.now()
    # 尝试从缓存获取
    cache_key = f'mall_active:flash:{now.year}:{now.month}:{now.day}:{request.user.is_vip if hasattr(request.user, "is_vip") else "false"}'
    flash_sale_products = None
    recommended_products = None
    user_marks = None
    
    try:
        from django.core.cache import caches
        cache = caches['mall_cache']
        cached_data = cache.get(cache_key)
        if cached_data:
            flash_sale_products = cached_data['products']
            recommended_products = cached_data['recommended']
            user_marks = cached_data['user_marks']
    except Exception as e:
        print(f"缓存读取失败: {e}")
    
    if flash_sale_products is None or recommended_products is None:
        current_flash_sales = FlashSale.objects.filter(
            status=True,
            start_time__lte=now,
            end_time__gte=now
        )

        # 获取秒杀商品
        flash_sale_products = []
        if current_flash_sales:
            # 从当前活动中获取所有秒杀商品
            flash_sale_product_ids = FlashSaleProduct.objects.filter(
                flash_sale__in=current_flash_sales
            ).values_list('product_id', flat=True)
            
            # 获取商品详情
            products_queryset = Product.objects.filter(
                id__in=flash_sale_product_ids,
                is_active=True,
                product_stock__gt=0
            ).order_by('-created_at')[:20]
            
            # 为商品添加discount属性
            for product in products_queryset:
                if product.old_price > product.price:
                    product.discount = int((1 - product.price / product.old_price) * 100)
                else:
                    product.discount = 0
                flash_sale_products.append(product)

        # 获取推荐商品
        recommended_queryset = Product.objects.filter(
            is_active=True,
            product_stock__gt=0
        ).exclude(id__in=[p.id for p in flash_sale_products]).order_by('?')[:5]
        
        # 为推荐商品添加discount属性
        recommended_products = []
        for product in recommended_queryset:
            if product.old_price > product.price:
                product.discount = int((1 - product.price / product.old_price) * 100)
            else:
                product.discount = 0
            recommended_products.append(product)

        # 获取用户收藏的商品
        user_marks = ProductMark.objects.filter(user=request.user).values_list('product_id', flat=True)
        
        # 缓存结果
        try:
            from django.core.cache import caches
            cache = caches['mall_cache']
            cache.set(cache_key, {
                'products': flash_sale_products,
                'recommended': recommended_products,
                'user_marks': user_marks
            }, 3600)  # 缓存1小时
        except Exception as e:
            print(f"缓存写入失败: {e}")

    # 创建一个虚拟的分类对象用于模板显示
    class VirtualCategory:
        def __init__(self):
            self.id = 0
            self.name = "秒杀活动"
            self.icon = None

    virtual_category = VirtualCategory()

    return render(request, 'mall/category_products.html', {
        'category': virtual_category,
        'products': flash_sale_products,
        'recommended_products': recommended_products,
        'user_marks': user_marks,
        'user': request.user
    })


# 优惠券页面
@login_required
def coupon_list(request):
    """优惠券页面"""
    # 获取优惠券状态
    status = request.GET.get('status', 'available')

    now = timezone.now()
    user_coupons = UserCoupon.objects.filter(user=request.user)

    # 按状态筛选
    if status == 'available':
        # 未使用且未过期
        user_coupons = user_coupons.filter(
            is_used=False,
            coupon__end_time__gte=now
        )
    elif status == 'used':
        # 已使用
        user_coupons = user_coupons.filter(is_used=True)
    elif status == 'expired':
        # 已过期
        user_coupons = user_coupons.filter(
            coupon__end_time__lt=now
        )

    # 获取可领取的优惠券
    available_coupons = Coupon.objects.filter(
        is_active=True,
        start_time__lte=now,
        end_time__gte=now,
        remaining_quantity__gt=0
    ).exclude(
        id__in=UserCoupon.objects.filter(
            user=request.user
        ).values_list('coupon_id', flat=True)
    )

    return render(request, 'mall/coupon_list.html', {
        'user_coupons': user_coupons,
        'available_coupons': available_coupons,
        'current_status': status
    })


# 地址管理页面
@login_required
def address_manage(request):
    """地址管理页面"""
    addresses = Address.objects.filter(user=request.user).order_by('-is_default', '-updated_at')

    return render(request, 'mall/address_manage.html', {
        'addresses': addresses
    })


# 添加地址
@login_required
@require_POST
def add_address(request):
    """添加地址"""
    try:
        # 获取地址信息
        recipient = request.POST.get('recipient')
        phone = request.POST.get('phone')
        province = request.POST.get('province')
        city = request.POST.get('city')
        district = request.POST.get('district')
        detail_address = request.POST.get('detail_address')
        is_default = request.POST.get('is_default') == 'true'

        # 创建地址
        address = Address.objects.create(
            user=request.user,
            recipient=recipient,
            phone=phone,
            province=province,
            city=city,
            district=district,
            detail_address=detail_address,
            is_default=is_default
        )

        return JsonResponse({'status': 'success', 'message': '地址添加成功'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


# 编辑地址
@login_required
@require_POST
def edit_address(request):
    """编辑地址"""
    try:
        address_id = request.POST.get('address_id')
        address = get_object_or_404(Address, id=address_id, user=request.user)

        # 更新地址信息
        address.recipient = request.POST.get('recipient', address.recipient)
        address.phone = request.POST.get('phone', address.phone)
        address.province = request.POST.get('province', address.province)
        address.city = request.POST.get('city', address.city)
        address.district = request.POST.get('district', address.district)
        address.detail_address = request.POST.get('detail_address', address.detail_address)
        address.is_default = request.POST.get('is_default') == 'true'
        address.save()

        return JsonResponse({'status': 'success', 'message': '地址更新成功'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


# 删除地址
@login_required
@require_POST
def delete_address(request):
    """删除地址"""
    try:
        address_id = request.POST.get('address_id')
        address = get_object_or_404(Address, id=address_id, user=request.user)
        address.delete()

        return JsonResponse({'status': 'success', 'message': '地址删除成功'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


# 物流查询页面
@login_required
def logistics_track(request, order_number):
    """物流查询页面"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    # 获取物流信息
    logistics = None
    trajectory = []

    if order.logistics_no:
        try:
            logistics = Logistics.objects.get(order=order)
            if logistics.trajectory:
                try:
                    trajectory = json.loads(logistics.trajectory)
                except:
                    pass
        except Logistics.DoesNotExist:
            pass

    return render(request, 'mall/logistics_track.html', {
        'order': order,
        'logistics': logistics,
        'trajectory': trajectory
    })


# 情侣专区页面
@login_required
def couple_zone(request):
    """情侣专区页面"""
    # 获取情侣款商品
    couple_products = Product.objects.filter(
        is_couple_product=True,
        is_active=True
    ).order_by('-created_at')[:12]

    # 获取情侣主题分类
    couple_categories = Category.objects.filter(
        is_active=True
    ).filter(
        name__icontains='情侣'
    )[:6]

    return render(request, 'mall/couple_zone.html', {
        'couple_products': couple_products,
        'couple_categories': couple_categories
    })


# 搜索结果页面
@login_required
def search_result(request):
    """搜索结果页面"""
    # 获取搜索关键词
    keyword = request.GET.get('keyword', '')

    # 搜索商品
    products = Product.objects.filter(
        is_active=True,
        name__icontains=keyword
    ) | Product.objects.filter(
        is_active=True,
        description__icontains=keyword
    )

    # 去重
    products = products.distinct().order_by('-created_at')

    return render(request, 'mall/search_result.html', {
        'products': products,
        'keyword': keyword
    })
