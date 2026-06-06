import logging

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.goods.models import Goods
from .models import Order, OrderAppeal
from .serializers import OrderAppealSerializer, OrderSerializer
from .utils.logistics import logistics_tool

User = get_user_model()
logger = logging.getLogger(__name__)


class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        goods_id = request.data.get("goods_id")
        receiver_name = request.data.get("receiver_name")
        receiver_phone = request.data.get("receiver_phone")
        receiver_address = request.data.get("receiver_address")

        if not all([goods_id, receiver_name, receiver_phone, receiver_address]):
            return Response({"code": 400, "msg": "收货信息或商品信息不完整"}, status=400)

        try:
            with transaction.atomic():
                goods = Goods.objects.select_for_update().get(id=goods_id)
                if goods.status != 1:
                    return Response({"code": 400, "msg": "商品已被抢购或下架"}, status=400)
                if goods.seller == request.user:
                    return Response({"code": 400, "msg": "不能购买自己发布的商品"}, status=400)

                existing_order = Order.objects.filter(goods=goods).exclude(status=4).first()
                if existing_order:
                    if existing_order.buyer == request.user and existing_order.status == 0:
                        existing_order.receiver_name = receiver_name
                        existing_order.receiver_phone = receiver_phone
                        existing_order.receiver_address = receiver_address
                        existing_order.save(update_fields=["receiver_name", "receiver_phone", "receiver_address"])
                        return Response({
                            "code": 200,
                            "msg": "您已拍下该商品，请尽快付款",
                            "data": {"order_id": existing_order.order_id, "amount": existing_order.amount},
                        })
                    return Response({"code": 400, "msg": "当前商品已经被其他用户拍下"}, status=400)

                cover = goods.images.filter(is_cover=True).first() or goods.images.first()
                new_order = Order.objects.create(
                    buyer=request.user,
                    seller=goods.seller,
                    goods=goods,
                    amount=goods.price,
                    receiver_name=receiver_name,
                    receiver_phone=receiver_phone,
                    receiver_address=receiver_address,
                    snapshot_content=goods.title,
                    snapshot_image=cover.image.url if cover else "",
                    status=0,
                )
            return Response({"code": 200, "msg": "下单成功", "data": {"order_id": new_order.order_id, "amount": new_order.amount}})
        except Goods.DoesNotExist:
            return Response({"code": 404, "msg": "商品不存在"}, status=404)
        except Exception:
            logger.exception("Failed to create order for user %s", request.user.id)
            return Response({"code": 500, "msg": "系统异常，请稍后重试"}, status=500)


class PayOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            with transaction.atomic():
                order = Order.objects.select_for_update().get(order_id=order_id, buyer=request.user)
                if order.status != 0:
                    return Response({"code": 400, "msg": "订单状态异常，可能已支付"}, status=400)

                locked_user = User.objects.select_for_update().get(id=request.user.id)
                if locked_user.balance < order.amount:
                    return Response({"code": 400, "msg": f"余额不足，当前余额 ￥{locked_user.balance}"}, status=400)

                locked_user.balance -= order.amount
                locked_user.save(update_fields=["balance"])
                order.status = 1
                order.pay_time = timezone.now()
                order.save(update_fields=["status", "pay_time"])

                if order.goods:
                    order.goods.status = 2
                    order.goods.save(update_fields=["status", "updated_at"])

            return Response({"code": 200, "msg": "支付成功，已通知卖家发货", "data": {"balance": locked_user.balance}})
        except Order.DoesNotExist:
            return Response({"code": 404, "msg": "订单不存在"}, status=404)
        except Exception:
            logger.exception("Failed to pay order %s", order_id)
            return Response({"code": 500, "msg": "支付系统异常，请稍后重试"}, status=500)


class MyOrderListView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Order.objects.filter(buyer=self.request.user).select_related("goods", "seller")
        status_param = self.request.query_params.get("status")
        if status_param is not None and status_param.strip() != "":
            queryset = queryset.filter(status=status_param)
        return queryset.order_by("-created_at")


class MySellOrderListView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Order.objects.filter(seller=self.request.user).select_related("goods", "buyer")
        status_param = self.request.query_params.get("status")
        if status_param is not None and status_param.strip() != "":
            queryset = queryset.filter(status=status_param)
        return queryset.order_by("-created_at")


class OrderLogisticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(order_id=order_id)
            if request.user != order.buyer and request.user != order.seller:
                return Response({"code": 403, "msg": "无权查看他人订单物流"}, status=403)

            if order.tracking_number == "SELF_PICKUP":
                return Response({
                    "code": 200,
                    "msg": "无需物流",
                    "data": [{"time": str(order.consign_time), "context": "卖家已选择线下自提/面交，请联系卖家完成交易。"}],
                })
            if not order.tracking_number:
                return Response({"code": 400, "msg": "该订单尚未发货，暂无单号"}, status=400)

            result = logistics_tool.get_track(order.tracking_number)
            if result["success"]:
                return Response({"code": 200, "msg": "获取物流成功", "company": result["company"], "data": result["data"]})
            return Response({"code": 500, "msg": f"查询失败: {result['msg']}"}, status=500)
        except Order.DoesNotExist:
            return Response({"code": 404, "msg": "订单不存在"}, status=404)


class ShipOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            delivery_method = int(request.data.get("delivery_method", 1))
        except (TypeError, ValueError):
            return Response({"code": 400, "msg": "发货方式参数错误"}, status=400)
        tracking_number = request.data.get("tracking_number")
        if delivery_method not in [1, 2]:
            return Response({"code": 400, "msg": "发货方式参数错误"}, status=400)

        try:
            with transaction.atomic():
                order = Order.objects.select_for_update().get(order_id=order_id, seller=request.user, status=1)
                if delivery_method == 2:
                    order.tracking_number = "SELF_PICKUP"
                else:
                    if not tracking_number:
                        return Response({"code": 400, "msg": "快递单号必填"}, status=400)
                    order.tracking_number = tracking_number
                order.status = 2
                order.consign_time = timezone.now()
                order.save(update_fields=["tracking_number", "status", "consign_time"])
            return Response({"code": 200, "msg": "发货处理成功"})
        except Order.DoesNotExist:
            return Response({"code": 404, "msg": "订单异常"}, status=404)


class ConfirmReceiptView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            with transaction.atomic():
                order = Order.objects.select_for_update().get(order_id=order_id, buyer=request.user, status=2)
                seller = User.objects.select_for_update().get(id=order.seller_id)
                seller.balance += order.amount
                seller.save(update_fields=["balance"])
                order.status = 3
                order.finish_time = timezone.now()
                order.save(update_fields=["status", "finish_time"])
                if order.goods:
                    order.goods.status = 2
                    order.goods.save(update_fields=["status", "updated_at"])

            return Response({
                "code": 200,
                "msg": "收货成功，款项已打入卖家余额",
                "data": {"final_status": "交易成功", "finish_time": order.finish_time},
            })
        except Order.DoesNotExist:
            return Response({"code": 404, "msg": "订单不存在或状态已变更，请刷新"}, status=404)
        except Exception:
            logger.exception("Failed to settle order %s", order_id)
            return Response({"code": 500, "msg": "结算异常，请稍后重试"}, status=500)


class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            with transaction.atomic():
                order = Order.objects.select_for_update().get(order_id=order_id, status__in=[0, 1])
                if request.user != order.buyer and request.user != order.seller:
                    return Response({"code": 403, "msg": "无权操作"}, status=403)
                if order.status == 1:
                    buyer = User.objects.select_for_update().get(id=order.buyer_id)
                    buyer.balance += order.amount
                    buyer.save(update_fields=["balance"])
                order.status = 4
                order.save(update_fields=["status"])
                if order.goods:
                    order.goods.status = 1
                    order.goods.save(update_fields=["status", "updated_at"])
            return Response({"code": 200, "msg": "订单已成功取消，商品已重新上架"})
        except Order.DoesNotExist:
            return Response({"code": 404, "msg": "订单无法取消，可能已发货或已完成"}, status=404)


class CreateOrderAppealView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        issue_type = request.data.get("issue_type", "").strip()
        description = request.data.get("description", "").strip()
        if not issue_type or not description:
            return Response({"code": 400, "msg": "请填写申诉类型和问题描述"}, status=400)

        try:
            with transaction.atomic():
                order = Order.objects.select_for_update().get(order_id=order_id)
                if request.user != order.buyer and request.user != order.seller:
                    return Response({"code": 403, "msg": "无权申诉该订单"}, status=403)
                if order.status not in [1, 2]:
                    return Response({"code": 400, "msg": "当前订单状态暂不支持申诉"}, status=400)
                if OrderAppeal.objects.filter(order=order, status__in=[0, 1]).exists():
                    return Response({"code": 400, "msg": "该订单已有待处理申诉"}, status=400)

                appeal = OrderAppeal.objects.create(
                    order=order,
                    applicant=request.user,
                    issue_type=issue_type,
                    description=description,
                    original_order_status=order.status,
                )
                order.status = 5
                order.save(update_fields=["status"])

            return Response({
                "code": 200,
                "msg": "申诉已提交，平台将尽快处理",
                "data": OrderAppealSerializer(appeal, context={"request": request}).data,
            })
        except Order.DoesNotExist:
            return Response({"code": 404, "msg": "订单不存在"}, status=404)


class MyOrderAppealListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        appeals = OrderAppeal.objects.select_related(
            "order", "order__buyer", "order__seller", "order__goods", "applicant", "handled_by"
        ).filter(Q(order__buyer=request.user) | Q(order__seller=request.user)).order_by("status", "-created_at")
        return Response({
            "code": 200,
            "msg": "获取申诉记录成功",
            "data": OrderAppealSerializer(appeals, many=True, context={"request": request}).data,
        })
