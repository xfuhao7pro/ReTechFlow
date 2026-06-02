from django.utils import timezone
import logging
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from apps.goods.models import Goods
from .models import Order
from django.contrib.auth import get_user_model

from .serializers import OrderSerializer
from .utils.logistics import logistics_tool

User = get_user_model()
logger = logging.getLogger(__name__)
class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        goods_id = request.data.get('goods_id')
        receiver_name = request.data.get('receiver_name')
        receiver_phone = request.data.get('receiver_phone')
        receiver_address = request.data.get('receiver_address')

        if not all([goods_id, receiver_name, receiver_phone, receiver_address]):
            return Response({"code": 400, "msg": "收货信息或商品信息不完整"}, status=400)

        # 开启数据库事务
        try:
            with transaction.atomic():
                # 在这行代码执行时，MySQL 会把这台相机的这行数据锁住，别的请求只能排队等
                goods = Goods.objects.select_for_update().get(id=goods_id)

                if goods.status != 1:
                    return Response({"code": 400, "msg": "手慢了，商品已被抢购或下架！"}, status=400)

                if goods.seller == request.user:
                    return Response({"code": 400, "msg": "不能购买自己发布的商品！"}, status=400)
                
                # 检查是否已经有人拍下（未付款或其他未结束状态）
                # 状态：0待付款，1待发货，2待收货，3交易成功，5售后/退款中
                # 只有状态为 4(交易取消) 的订单才允许其他人再次购买
                existing_order = Order.objects.filter(goods=goods).exclude(status=4).first()
                if existing_order:
                    if existing_order.buyer == request.user and existing_order.status == 0:
                        # 如果是当前用户自己拍下的且未付款，直接更新收货信息并返回该订单
                        existing_order.receiver_name = receiver_name
                        existing_order.receiver_phone = receiver_phone
                        existing_order.receiver_address = receiver_address
                        existing_order.save()
                        return Response({
                            "code": 200,
                            "msg": "您已拍下该商品，请尽快付款",
                            "data": {
                                "order_id": existing_order.order_id,
                                "amount": existing_order.amount
                            }
                        })
                    else:
                        return Response({"code": 400, "msg": "当前已经有小伙伴拍下了哦过会再看看吧"}, status=400)

                # 获取商品快照图
                cover = goods.images.filter(is_cover=True).first()
                if not cover:
                    cover = goods.images.first()
                cover_url = cover.image.url if cover else ""

                new_order = Order.objects.create(
                    buyer=request.user,
                    seller=goods.seller,
                    goods=goods,
                    amount=goods.price,
                    receiver_name=receiver_name,
                    receiver_phone=receiver_phone,
                    receiver_address=receiver_address,
                    snapshot_content=goods.title,
                    snapshot_image=cover_url,
                    status=0  # 状态 0 代表待付款
                )

            return Response({
                "code": 200,
                "msg": "下单成功",
                "data": {
                    "order_id": new_order.order_id,
                    "amount": new_order.amount
                }
            })

        except Goods.DoesNotExist:
            return Response({"code": 404, "msg": "商品不存在"}, status=404)
        except Exception:
            logger.exception("Failed to create order for user %s", request.user.id)
            return Response({"code": 500, "msg": "系统异常，请稍后重试"}, status=500)

class PayOrderView(APIView):
    """
    余额支付接口（直连 User 表版）
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            # 开启数据库事务：扣钱和改订单状态必须同生共死！
            with transaction.atomic():
                # 1. 锁订单：防止同一个订单被重复点击支付
                order = Order.objects.select_for_update().get(order_id=order_id, buyer=request.user)

                if order.status != 0:
                    return Response({"code": 400, "msg": "订单状态异常，可能已支付"}, status=400)

                # 👉 2. 核心细节：强行重查 User 并上悲观锁！
                # 绝不能直接用 request.user.balance 扣钱
                locked_user = User.objects.select_for_update().get(id=request.user.id)

                # 3. 校验余额
                if locked_user.balance < order.amount:
                    return Response({"code": 400, "msg": f"余额不足！当前余额: ¥{locked_user.balance}"}, status=400)

                # 4. 核心逻辑：扣钱
                locked_user.balance -= order.amount
                locked_user.save()

                # 5. 更新订单状态
                order.status = 1  # 状态流转为：待发货
                order.pay_time = timezone.now()
                order.save()

                # 6. 更新商品状态为已售出，从交易广场消失
                if order.goods:
                    order.goods.status = 2
                    order.goods.save()

            return Response({
                "code": 200,
                "msg": "支付成功！已通知卖家发货",
                "data": {
                    "balance": locked_user.balance  # 返回最新余额给前端
                }
            })

        except Order.DoesNotExist:
            return Response({"code": 404, "msg": "订单不存在"}, status=404)
        except Exception:
            logger.exception("Failed to pay order %s", order_id)
            return Response({"code": 500, "msg": "支付系统异常，请稍后重试"}, status=500)

class MyOrderListView(ListAPIView):
    """
    获取当前用户的订单列表
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Order.objects.filter(buyer=self.request.user).select_related('goods', 'seller')
        status_param = self.request.query_params.get('status')
        if status_param is not None and status_param.strip() != '':
            queryset = queryset.filter(status=status_param)
        return queryset.order_by('-created_at')

class MySellOrderListView(ListAPIView):
    """
    获取当前用户【卖出】的订单列表
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Order.objects.filter(seller=self.request.user).select_related('goods', 'buyer')
        status_param = self.request.query_params.get('status')
        if status_param is not None and status_param.strip() != '':
            queryset = queryset.filter(status=status_param)
        return queryset.order_by('-created_at')


class OrderLogisticsView(APIView):
    """
    查看订单物流轨迹
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(order_id=order_id)
            if request.user != order.buyer and request.user != order.seller:
                return Response({"code": 403, "msg": "无权查看他人订单物流"}, status=403)

            if order.tracking_number == 'SELF_PICKUP':
                return Response({
                    "code": 200,
                    "msg": "无需物流",
                    "data": [
                        {"time": str(order.consign_time), "context": "卖家已选择线下自提/面交，请联系卖家完成交易。"}
                    ]
                })

            if not order.tracking_number:
                return Response({"code": 400, "msg": "该订单尚未发货，暂无单号"}, status=400)

            result = logistics_tool.get_track(order.tracking_number)

            if result['success']:
                return Response({
                    "code": 200,
                    "msg": "获取物流成功",
                    "company": result['company'], # 快递100自动识别的公司名
                    "data": result['data']        # 包含 time 和 context 的轨迹列表
                })
            else:
                return Response({
                    "code": 500,
                    "msg": f"查询失败: {result['msg']}"
                }, status=500)

        except Order.DoesNotExist:
            return Response({"code": 404, "msg": "订单不存在"}, status=404)


class ShipOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        # 前端传一个 delivery_method：1 代表快递，2 代表自提
        try:
            delivery_method = int(request.data.get('delivery_method', 1))
        except (TypeError, ValueError):
            return Response({"code": 400, "msg": "发货方式参数错误"}, status=400)

        tracking_number = request.data.get('tracking_number')

        if delivery_method not in [1, 2]:
            return Response({"code": 400, "msg": "发货方式参数错误"}, status=400)

        try:
            with transaction.atomic():
                order = Order.objects.select_for_update().get(order_id=order_id, seller=request.user, status=1)

                if delivery_method == 2:
                    order.tracking_number = 'SELF_PICKUP'
                else:
                    if not tracking_number:
                        return Response({"code": 400, "msg": "快递单号必填"}, status=400)
                    order.tracking_number = tracking_number

                order.status = 2
                order.consign_time = timezone.now()
                order.save()
            return Response({"code": 200, "msg": "发货处理成功"})
        except Order.DoesNotExist:
            return Response({"code": 404, "msg": "订单异常"}, status=404)

class ConfirmReceiptView(APIView):
    """
    买家确认收货：触发资金结算，钱入卖家钱包
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            # 开启数据库事务，保证状态修改和资金增加要么全成功，要么全回滚
            with transaction.atomic():
                # 锁订单：必须是当前买家的订单，且状态必须是“待收货”
                # 使用select_for_update()防止买家手抖点快了导致二次结算
                order = Order.objects.select_for_update().get(
                    order_id=order_id,
                    buyer=request.user,
                    status=2
                )

                seller = User.objects.select_for_update().get(id=order.seller.id)

                seller.balance += order.amount
                seller.save()

                order.status = 3
                order.finish_time = timezone.now()
                order.save()

                if order.goods:
                    order.goods.status = 2
                    order.goods.save()

            return Response({
                "code": 200,
                "msg": "收货成功，钱款已打入卖家余额！",
                "data": {
                    "final_status": "交易成功",
                    "finish_time": order.finish_time
                }
            })

        except Order.DoesNotExist:
            return Response({"code": 404, "msg": "订单不存在或状态已变更，请刷新"}, status=404)
        except Exception:
            # 这里的报错会被 transaction.atomic 自动回滚，不用担心钱加了一半
            logger.exception("Failed to settle order %s", order_id)
            return Response({"code": 500, "msg": "结算异常，请稍后重试"}, status=500)


class CancelOrderView(APIView):
    """
    取消订单：释放商品，状态变取消
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            with transaction.atomic():
                # 只能取消“待付款(0)”或“待发货(1)”的订单
                # 如果是已发货，就不能随便取消了，得走退款流程
                order = Order.objects.select_for_update().get(
                    order_id=order_id,
                    status__in=[0, 1]
                )

                # 权限校验：买家或卖家才能取消
                if request.user != order.buyer and request.user != order.seller:
                    return Response({"msg": "无权操作"}, status=403)

                # 1. 如果已经付过钱了（status=1），取消时还要退钱给买家
                if order.status == 1:
                    buyer = User.objects.select_for_update().get(id=order.buyer_id)
                    buyer.balance += order.amount
                    buyer.save()
                    # 记录一笔退款流水

                order.status = 4
                order.save()

                if order.goods:
                    order.goods.status = 1  #重新回到“在售”状态
                    order.goods.save()

            return Response({"code": 200, "msg": "订单已成功取消，商品已重新上架"})
        except Order.DoesNotExist:
            return Response({"msg": "订单无法取消（可能已发货或已完成）"}, status=404)
