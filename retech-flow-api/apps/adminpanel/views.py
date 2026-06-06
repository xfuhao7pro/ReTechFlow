from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.chats.models import SystemAnnouncement
from apps.chats.serializers import SystemAnnouncementSerializer
from apps.goods.models import Category, CategoryAttribute, Goods, GoodsStatusChoices
from apps.goods.serializers import GoodsSerializer
from apps.orders.models import Order
from apps.orders.serializers import OrderSerializer
from apps.users.models import IdentityVerificationStatusChoices, UserRoleChoices

User = get_user_model()


def api_response(data=None, msg="ok", code=200, status=200):
    return Response({"code": code, "msg": msg, "data": data}, status=status)


def is_admin_user(user):
    return bool(user and user.is_authenticated and user.role in [UserRoleChoices.AUDITOR, UserRoleChoices.ADMIN])


def is_super_admin(user):
    return bool(user and user.is_authenticated and user.role == UserRoleChoices.ADMIN)


class IsAdminUserRole(BasePermission):
    message = "无后台访问权限"

    def has_permission(self, request, view):
        return is_admin_user(request.user)


class IsSuperAdminRole(BasePermission):
    message = "仅系统管理员可操作"

    def has_permission(self, request, view):
        return is_super_admin(request.user)


class AdminPermissionMixin:
    permission_classes = [IsAuthenticated, IsAdminUserRole]


class SuperAdminPermissionMixin:
    permission_classes = [IsAuthenticated, IsSuperAdminRole]


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
    end = start + page_size
    return queryset[start:end], {"page": page, "page_size": page_size, "total": total}


def identity_user_payload(user):
    return {
        "id": user.id,
        "email": user.email,
        "nickname": user.nickname,
        "avatar": user.avatar,
        "is_verified": user.is_verified,
        "verification_status": user.verification_status,
        "verification_status_text": user.get_verification_status_display(),
        "verification_reject_reason": user.verification_reject_reason,
        "real_name": user.real_name,
        "id_card": user.id_card,
        "date_joined": user.date_joined,
    }


def category_payload(category):
    return {
        "id": category.id,
        "name": category.name,
        "sort": category.sort,
        "goods_count": getattr(category, "goods_count", 0),
        "attributes": [
            {
                "id": attr.id,
                "name": attr.name,
                "options": attr.options or [],
            }
            for attr in category.attributes.all()
        ],
    }


def daily_count_payload(queryset, date_field, days=14):
    start_date = date.today() - timedelta(days=days - 1)
    rows = (
        queryset.filter(**{f"{date_field}__date__gte": start_date})
        .annotate(day=TruncDate(date_field))
        .values("day")
        .annotate(count=Count("pk"))
        .order_by("day")
    )
    count_map = {row["day"]: row["count"] for row in rows}
    return [
        {
            "date": (start_date + timedelta(days=index)).strftime("%m-%d"),
            "count": count_map.get(start_date + timedelta(days=index), 0),
        }
        for index in range(days)
    ]


def daily_amount_payload(queryset, date_field, days=14):
    start_date = date.today() - timedelta(days=days - 1)
    rows = (
        queryset.filter(**{f"{date_field}__date__gte": start_date})
        .annotate(day=TruncDate(date_field))
        .values("day")
        .annotate(amount=Sum("amount"))
        .order_by("day")
    )
    amount_map = {row["day"]: float(row["amount"] or 0) for row in rows}
    return [
        {
            "date": (start_date + timedelta(days=index)).strftime("%m-%d"),
            "amount": amount_map.get(start_date + timedelta(days=index), 0),
        }
        for index in range(days)
    ]


class AdminDashboardView(AdminPermissionMixin, APIView):
    def get(self, request):
        goods_status = {
            str(item["status"]): item["count"]
            for item in Goods.objects.values("status").annotate(count=Count("id"))
        }
        order_status = {
            str(item["status"]): item["count"]
            for item in Order.objects.values("status").annotate(count=Count("order_id"))
        }
        data = {
            "role": request.user.role,
            "cards": {
                "users": User.objects.count(),
                "goods": Goods.objects.count(),
                "pending_review_goods": Goods.objects.filter(status=GoodsStatusChoices.PENDING_REVIEW).count(),
                "on_sale_goods": Goods.objects.filter(status=GoodsStatusChoices.ON_SALE).count(),
                "orders": Order.objects.count(),
                "pending_ship_orders": Order.objects.filter(status=1).count(),
                "pending_identity": User.objects.filter(
                    verification_status=IdentityVerificationStatusChoices.PENDING
                ).count(),
            },
            "goods_status": goods_status,
            "order_status": order_status,
            "recent_goods": GoodsSerializer(
                Goods.objects.select_related("seller", "category").prefetch_related("images").order_by("-created_at")[:5],
                many=True,
                context={"request": request},
            ).data,
            "recent_orders": OrderSerializer(
                Order.objects.select_related("buyer", "seller", "goods").order_by("-created_at")[:5],
                many=True,
                context={"request": request},
            ).data,
        }
        return api_response(data, "获取后台概览成功")


class AdminGoodsListView(AdminPermissionMixin, APIView):
    def get(self, request):
        queryset = Goods.objects.select_related("seller", "category").prefetch_related("images").order_by("-created_at")
        status_value = request.query_params.get("status")
        keyword = request.query_params.get("keyword", "").strip()
        if status_value not in [None, "", "all"]:
            queryset = queryset.filter(status=status_value)
        if keyword:
            queryset = queryset.filter(Q(title__icontains=keyword) | Q(seller__nickname__icontains=keyword))
        page_items, page_info = paginate_queryset(request, queryset)
        return api_response({
            "list": GoodsSerializer(page_items, many=True, context={"request": request}).data,
            **page_info,
        }, "获取商品列表成功")


class AdminGoodsStatusView(AdminPermissionMixin, APIView):
    def post(self, request, goods_id):
        goods = get_object_or_404(Goods, id=goods_id)
        status_value = parse_int(request.data.get("status"))
        if status_value not in [0, 1, 2, 3, 4, 5]:
            return api_response(None, "商品状态不合法", 400, 400)
        goods.status = status_value
        goods.audit_reason = request.data.get("audit_reason", "").strip()
        goods.save(update_fields=["status", "audit_reason", "updated_at"])
        return api_response(GoodsSerializer(goods, context={"request": request}).data, "商品状态已更新")


class AdminOrderListView(AdminPermissionMixin, APIView):
    def get(self, request):
        queryset = Order.objects.select_related("buyer", "seller", "goods").order_by("-created_at")
        status_value = request.query_params.get("status")
        keyword = request.query_params.get("keyword", "").strip()
        if status_value not in [None, "", "all"]:
            queryset = queryset.filter(status=status_value)
        if keyword:
            queryset = queryset.filter(
                Q(order_id__icontains=keyword)
                | Q(goods__title__icontains=keyword)
                | Q(buyer__nickname__icontains=keyword)
                | Q(seller__nickname__icontains=keyword)
            )
        page_items, page_info = paginate_queryset(request, queryset)
        return api_response({
            "list": OrderSerializer(page_items, many=True, context={"request": request}).data,
            **page_info,
        }, "获取订单列表成功")


class AdminIdentityListView(AdminPermissionMixin, APIView):
    def get(self, request):
        queryset = User.objects.exclude(
            verification_status=IdentityVerificationStatusChoices.NOT_SUBMITTED
        ).order_by("verification_status", "-date_joined")
        status_value = request.query_params.get("status", IdentityVerificationStatusChoices.PENDING)
        keyword = request.query_params.get("keyword", "").strip()
        if status_value not in [None, "", "all"]:
            queryset = queryset.filter(verification_status=status_value)
        if keyword:
            queryset = queryset.filter(
                Q(email__icontains=keyword)
                | Q(nickname__icontains=keyword)
                | Q(real_name__icontains=keyword)
                | Q(id_card__icontains=keyword)
            )
        page_items, page_info = paginate_queryset(request, queryset)
        return api_response({
            "list": [identity_user_payload(user) for user in page_items],
            **page_info,
        }, "获取实名认证审核列表成功")


class AdminUserListView(SuperAdminPermissionMixin, APIView):
    def get(self, request):
        queryset = User.objects.order_by("-date_joined")
        role = request.query_params.get("role")
        keyword = request.query_params.get("keyword", "").strip()
        if role not in [None, "", "all"]:
            queryset = queryset.filter(role=role)
        if keyword:
            queryset = queryset.filter(Q(email__icontains=keyword) | Q(nickname__icontains=keyword))
        page_items, page_info = paginate_queryset(request, queryset)
        data = []
        for user in page_items:
            data.append({
                "id": user.id,
                "email": user.email,
                "nickname": user.nickname,
                "avatar": user.avatar,
                "role": user.role,
                "role_text": user.get_role_display(),
                "is_active": user.is_active,
                "is_staff": user.is_staff,
                "balance": str(user.balance),
                "date_joined": user.date_joined,
            })
        return api_response({"list": data, **page_info}, "获取用户列表成功")


class AdminUserRoleView(SuperAdminPermissionMixin, APIView):
    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        role = parse_int(request.data.get("role"))
        if role not in [UserRoleChoices.NORMAL_USER, UserRoleChoices.AUDITOR, UserRoleChoices.ADMIN]:
            return api_response(None, "角色不合法", 400, 400)
        user.role = role
        user.is_staff = role in [UserRoleChoices.AUDITOR, UserRoleChoices.ADMIN]
        user.is_superuser = role == UserRoleChoices.ADMIN
        user.save(update_fields=["role", "is_staff", "is_superuser"])
        return api_response({"id": user.id, "role": user.role, "role_text": user.get_role_display()}, "用户角色已更新")


class AdminUserStatusView(SuperAdminPermissionMixin, APIView):
    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        if user.id == request.user.id:
            return api_response(None, "不能禁用当前登录账号", 400, 400)
        is_active = bool(request.data.get("is_active"))
        user.is_active = is_active
        user.save(update_fields=["is_active"])
        return api_response({"id": user.id, "is_active": user.is_active}, "用户状态已更新")


class AdminUserVerifyView(AdminPermissionMixin, APIView):
    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        action = request.data.get("action")
        reason = request.data.get("reason", "").strip()
        if action == "approve":
            if not user.real_name or not user.id_card:
                return api_response(None, "用户未提交实名认证资料", 400, 400)
            user.is_verified = True
            user.verification_status = IdentityVerificationStatusChoices.APPROVED
            user.verification_reject_reason = ""
        elif action == "reject":
            if not reason:
                return api_response(None, "驳回时必须填写原因", 400, 400)
            user.is_verified = False
            user.verification_status = IdentityVerificationStatusChoices.REJECTED
            user.verification_reject_reason = reason
        else:
            return api_response(None, "审核动作不合法", 400, 400)
        user.save(update_fields=["is_verified", "verification_status", "verification_reject_reason"])
        return api_response(identity_user_payload(user), "实名认证审核已处理")


class AdminDashboardView(AdminPermissionMixin, APIView):
    def get(self, request):
        paid_orders = Order.objects.filter(status__in=[1, 2, 3, 5])
        goods_status = {
            str(item["status"]): item["count"]
            for item in Goods.objects.values("status").annotate(count=Count("id"))
        }
        order_status = {
            str(item["status"]): item["count"]
            for item in Order.objects.values("status").annotate(count=Count("order_id"))
        }
        category_rank = [
            {"name": item["category__name"] or "未分类", "count": item["count"]}
            for item in Goods.objects.values("category__name").annotate(count=Count("id")).order_by("-count")[:8]
        ]
        user_roles = {
            str(item["role"]): item["count"]
            for item in User.objects.values("role").annotate(count=Count("id"))
        }
        identity_status = {
            str(item["verification_status"]): item["count"]
            for item in User.objects.values("verification_status").annotate(count=Count("id"))
        }
        data = {
            "role": request.user.role,
            "cards": {
                "users": User.objects.count(),
                "goods": Goods.objects.count(),
                "pending_review_goods": Goods.objects.filter(status=GoodsStatusChoices.PENDING_REVIEW).count(),
                "on_sale_goods": Goods.objects.filter(status=GoodsStatusChoices.ON_SALE).count(),
                "orders": Order.objects.count(),
                "pending_ship_orders": Order.objects.filter(status=1).count(),
                "pending_identity": User.objects.filter(
                    verification_status=IdentityVerificationStatusChoices.PENDING
                ).count(),
                "paid_amount": float(paid_orders.aggregate(total=Sum("amount"))["total"] or 0),
                "active_announcements": SystemAnnouncement.objects.filter(is_active=True).count(),
            },
            "goods_status": goods_status,
            "order_status": order_status,
            "charts": {
                "user_trend": daily_count_payload(User.objects.all(), "date_joined"),
                "goods_trend": daily_count_payload(Goods.objects.all(), "created_at"),
                "order_trend": daily_count_payload(Order.objects.all(), "created_at"),
                "amount_trend": daily_amount_payload(paid_orders, "created_at"),
                "category_rank": category_rank,
                "user_roles": user_roles,
                "identity_status": identity_status,
            },
            "todo": {
                "pending_goods": Goods.objects.filter(status=GoodsStatusChoices.PENDING_REVIEW).count(),
                "pending_identity": User.objects.filter(
                    verification_status=IdentityVerificationStatusChoices.PENDING
                ).count(),
                "pending_ship_orders": Order.objects.filter(status=1).count(),
                "after_sale_orders": Order.objects.filter(status=5).count(),
            },
            "recent_goods": GoodsSerializer(
                Goods.objects.select_related("seller", "category").prefetch_related("images").order_by("-created_at")[:5],
                many=True,
                context={"request": request},
            ).data,
            "recent_orders": OrderSerializer(
                Order.objects.select_related("buyer", "seller", "goods").order_by("-created_at")[:5],
                many=True,
                context={"request": request},
            ).data,
            "recent_announcements": SystemAnnouncementSerializer(
                SystemAnnouncement.objects.select_related("created_by").order_by("-created_at")[:5],
                many=True,
            ).data,
        }
        return api_response(data, "获取后台数据大屏成功")


class AdminUserRoleView(SuperAdminPermissionMixin, APIView):
    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        if user.id == request.user.id:
            return api_response(None, "不能修改当前登录账号的角色", 400, 400)
        role = parse_int(request.data.get("role"))
        if role not in [UserRoleChoices.NORMAL_USER, UserRoleChoices.AUDITOR, UserRoleChoices.ADMIN]:
            return api_response(None, "角色不合法", 400, 400)
        user.role = role
        user.is_staff = role in [UserRoleChoices.AUDITOR, UserRoleChoices.ADMIN]
        user.is_superuser = role == UserRoleChoices.ADMIN
        user.save(update_fields=["role", "is_staff", "is_superuser"])
        return api_response({"id": user.id, "role": user.role, "role_text": user.get_role_display()}, "用户角色已更新")


class AdminUserPasswordResetView(SuperAdminPermissionMixin, APIView):
    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        password = request.data.get("password", "").strip()
        if len(password) < 6:
            return api_response(None, "新密码至少 6 位", 400, 400)
        user.set_password(password)
        user.save(update_fields=["password"])
        return api_response({"id": user.id}, "用户密码已重置")


class AdminCategoryListView(AdminPermissionMixin, APIView):
    def get(self, request):
        categories = Category.objects.annotate(goods_count=Count("goods")).prefetch_related("attributes").order_by("sort", "id")
        return api_response([category_payload(category) for category in categories], "获取分类配置成功")

    def post(self, request):
        name = request.data.get("name", "").strip()
        sort = parse_int(request.data.get("sort"), 0)
        if not name:
            return api_response(None, "分类名称不能为空", 400, 400)
        category = Category.objects.create(name=name, sort=sort)
        return api_response(category_payload(category), "分类已添加")


class AdminCategoryDetailView(AdminPermissionMixin, APIView):
    def put(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        name = request.data.get("name", "").strip()
        sort = parse_int(request.data.get("sort"), category.sort)
        if not name:
            return api_response(None, "分类名称不能为空", 400, 400)
        category.name = name
        category.sort = sort
        category.save(update_fields=["name", "sort"])
        category.goods_count = Goods.objects.filter(category=category).count()
        return api_response(category_payload(category), "分类已更新")

    def delete(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        if Goods.objects.filter(category=category).exists():
            return api_response(None, "该分类下已有商品，不能删除", 400, 400)
        category.delete()
        return api_response(None, "分类已删除")


class AdminCategoryAttributeView(AdminPermissionMixin, APIView):
    def post(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        name = request.data.get("name", "").strip()
        options = request.data.get("options") or []
        if not name:
            return api_response(None, "属性名称不能为空", 400, 400)
        if not isinstance(options, list):
            return api_response(None, "属性选项必须是数组", 400, 400)
        attr = CategoryAttribute.objects.create(category=category, name=name, options=options)
        return api_response({"id": attr.id, "name": attr.name, "options": attr.options}, "属性已添加")

    def put(self, request, category_id, attr_id):
        attr = get_object_or_404(CategoryAttribute, id=attr_id, category_id=category_id)
        name = request.data.get("name", "").strip()
        options = request.data.get("options") or []
        if not name:
            return api_response(None, "属性名称不能为空", 400, 400)
        if not isinstance(options, list):
            return api_response(None, "属性选项必须是数组", 400, 400)
        attr.name = name
        attr.options = options
        attr.save(update_fields=["name", "options"])
        return api_response({"id": attr.id, "name": attr.name, "options": attr.options}, "属性已更新")

    def delete(self, request, category_id, attr_id):
        attr = get_object_or_404(CategoryAttribute, id=attr_id, category_id=category_id)
        attr.delete()
        return api_response(None, "属性已删除")


class AdminAnnouncementListView(AdminPermissionMixin, APIView):
    def get(self, request):
        queryset = SystemAnnouncement.objects.select_related("created_by").order_by("-created_at")
        page_items, page_info = paginate_queryset(request, queryset)
        return api_response({
            "list": SystemAnnouncementSerializer(page_items, many=True).data,
            **page_info,
        }, "获取公告列表成功")

    def post(self, request):
        title = request.data.get("title", "").strip()
        content = request.data.get("content", "").strip()
        is_active = bool(request.data.get("is_active", True))
        if not title or not content:
            return api_response(None, "公告标题和内容不能为空", 400, 400)
        notice = SystemAnnouncement.objects.create(
            title=title,
            content=content,
            is_active=is_active,
            created_by=request.user,
        )
        return api_response(SystemAnnouncementSerializer(notice).data, "公告已发布")


class AdminAnnouncementDetailView(AdminPermissionMixin, APIView):
    def put(self, request, notice_id):
        notice = get_object_or_404(SystemAnnouncement, id=notice_id)
        title = request.data.get("title", "").strip()
        content = request.data.get("content", "").strip()
        if not title or not content:
            return api_response(None, "公告标题和内容不能为空", 400, 400)
        notice.title = title
        notice.content = content
        notice.is_active = bool(request.data.get("is_active", notice.is_active))
        notice.save(update_fields=["title", "content", "is_active", "updated_at"])
        return api_response(SystemAnnouncementSerializer(notice).data, "公告已更新")

    def delete(self, request, notice_id):
        notice = get_object_or_404(SystemAnnouncement, id=notice_id)
        notice.delete()

        return api_response(None, "公告已删除")
