from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.goods.models import GoodsStatusChoices
from apps.orders.models import Order, OrderAppeal
from apps.orders.serializers import OrderAppealSerializer
from apps.users.models import UserRoleChoices

User = get_user_model()


def api_response(data=None, msg="ok", code=200, status=200):
    return Response({"code": code, "msg": msg, "data": data}, status=status)


class IsAdminUserRole(BasePermission):
    message = "无后台访问权限"

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in [UserRoleChoices.AUDITOR, UserRoleChoices.ADMIN]
        )


class AdminPermissionMixin:
    permission_classes = [IsAuthenticated, IsAdminUserRole]


def parse_int(value, default=None):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def paginate_queryset(request, queryset):
    page = max(parse_int(request.query_params.get("page"), 1), 1)
    page_size = min(max(parse_int(request.query_params.get("page_size"), 10), 1), 50)
    total = queryset.count()
    start = (page - 1) * page_size
    return queryset[start:start + page_size], {"page": page, "page_size": page_size, "total": total}


class AdminAppealListView(AdminPermissionMixin, APIView):
    def get(self, request):
        queryset = OrderAppeal.objects.select_related(
            "order", "order__buyer", "order__seller", "order__goods", "applicant", "handled_by"
        ).order_by("status", "-created_at")
        status_value = request.query_params.get("status")
        keyword = request.query_params.get("keyword", "").strip()
        if status_value not in [None, "", "all"]:
            queryset = queryset.filter(status=status_value)
        if keyword:
            queryset = queryset.filter(
                Q(order__order_id__icontains=keyword)
                | Q(order__goods__title__icontains=keyword)
                | Q(order__buyer__nickname__icontains=keyword)
                | Q(order__seller__nickname__icontains=keyword)
                | Q(applicant__nickname__icontains=keyword)
                | Q(issue_type__icontains=keyword)
            )
        page_items, page_info = paginate_queryset(request, queryset)
        return api_response({
            "list": OrderAppealSerializer(page_items, many=True, context={"request": request}).data,
            **page_info,
        }, "获取申诉列表成功")


class AdminAppealResolveView(AdminPermissionMixin, APIView):
    def post(self, request, appeal_id):
        result = request.data.get("result", "").strip()
        remark = request.data.get("admin_remark", "").strip()
        if result not in ["refund_buyer", "release_seller", "close"]:
            return api_response(None, "裁决结果不合法", 400, 400)
        if not remark:
            return api_response(None, "请填写处理备注", 400, 400)

        try:
            with transaction.atomic():
                appeal = OrderAppeal.objects.select_for_update().select_related(
                    "order", "order__buyer", "order__seller", "order__goods", "applicant"
                ).get(id=appeal_id)
                if appeal.status in [2, 3]:
                    return api_response(None, "该申诉已处理，不能重复裁决", 400, 400)

                order = Order.objects.select_for_update().get(order_id=appeal.order.order_id)
                buyer = User.objects.select_for_update().get(id=order.buyer_id)
                seller = User.objects.select_for_update().get(id=order.seller_id)

                if result == "refund_buyer":
                    buyer.balance += order.amount
                    buyer.save(update_fields=["balance"])
                    order.status = 4
                    if order.goods:
                        order.goods.status = GoodsStatusChoices.OFF_SHELVES
                        order.goods.save(update_fields=["status", "updated_at"])
                elif result == "release_seller":
                    seller.balance += order.amount
                    seller.save(update_fields=["balance"])
                    order.status = 3
                    order.finish_time = timezone.now()
                    if order.goods:
                        order.goods.status = GoodsStatusChoices.SOLD
                        order.goods.save(update_fields=["status", "updated_at"])
                else:
                    order.status = appeal.original_order_status

                order.save(update_fields=["status", "finish_time"] if result == "release_seller" else ["status"])
                appeal.status = 2 if result in ["refund_buyer", "release_seller"] else 3
                appeal.result = result
                appeal.admin_remark = remark
                appeal.handled_by = request.user
                appeal.handled_at = timezone.now()
                appeal.save(update_fields=["status", "result", "admin_remark", "handled_by", "handled_at", "updated_at"])

            return api_response(
                OrderAppealSerializer(appeal, context={"request": request}).data,
                "申诉已处理",
            )
        except OrderAppeal.DoesNotExist:
            return api_response(None, "申诉不存在", 404, 404)
