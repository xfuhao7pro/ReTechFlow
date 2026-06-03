import uuid
import asyncio
import json
import logging
import re
import threading
from django.core.files.storage import default_storage
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
import os

from .models import Category, Goods, GoodsLike, GoodsStatusChoices
from .utils.ai_valuation import evaluate_3c_goods,is_3c_product_by_llm
from  .serializers import GoodsSerializer,CategorySerializer
from .utils.file_clean import clean_expired_temp_files
from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)

VALUATION_TASK_TTL = 3600  # Redis 过期时间（秒）
GUEST_VALUATION_TTL = 365 * 24 * 3600
GUEST_TOKEN_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{16,80}$")


def _build_redis_key(task_id: str) -> str:
    return f"valuation:task:{task_id}"


def _get_guest_token(request) -> str:
    token = request.headers.get("X-Guest-Token", "").strip()
    return token if GUEST_TOKEN_PATTERN.fullmatch(token) else ""


def _get_request_owner(request) -> str:
    if request.user and request.user.is_authenticated:
        return str(request.user.id)
    guest_token = _get_guest_token(request)
    return f"guest_{guest_token}" if guest_token else ""


def _get_request_owners(request) -> set[str]:
    owners = {_get_request_owner(request)}
    guest_token = _get_guest_token(request)
    if guest_token:
        owners.add(f"guest_{guest_token}")
    return {owner for owner in owners if owner}

def _run_valuation_sync(task_id: str, user_id: str, user_desc: str, valid_image_paths: list):
    """
    同步执行 AI 估价（风控 + 估价），完成后更新 Redis 状态。
    此函数会在 asyncio.to_thread() 中运行，不阻塞事件循环。
    """
    redis_key = _build_redis_key(task_id)

    try:
        # 风控安检
        logger.info("Valuation task %s: starting safety check", task_id)
        is_pass = is_3c_product_by_llm(valid_image_paths)
        if not is_pass:
            cache.set(redis_key, json.dumps({
                "user_id": user_id,
                "status": "失败",
                "msg": "安检未通过：您上传的图片似乎均非数码产品！",
                "data": None
            }), VALUATION_TASK_TTL)
            return {"status": "失败", "msg": "安检未通过：您上传的图片似乎均非数码产品！"}

        # AI 估价
        logger.info("Valuation task %s: requesting AI valuation", task_id)
        result = evaluate_3c_goods(user_desc=user_desc, image_paths=valid_image_paths)

        if result:
            cache.set(redis_key, json.dumps({
                "user_id": user_id,
                "status": "成功",
                "msg": "AI 估价成功！",
                "data": result
            }), VALUATION_TASK_TTL)
            return {"status": "成功", "data": result}
        else:
            cache.set(redis_key, json.dumps({
                "user_id": user_id,
                "status": "失败",
                "msg": "系统开小差了，请重试。",
                "data": None
            }), VALUATION_TASK_TTL)
            return {"status": "失败", "msg": "系统开小差了，请重试。"}

    except ValueError as e:
        logger.warning("Valuation task %s rejected: %s", task_id, e)
        public_message = "AI 服务暂时不可用，请稍后重试"
        cache.set(redis_key, json.dumps({
            "user_id": user_id,
            "status": "失败",
            "msg": public_message,
            "data": None
        }), VALUATION_TASK_TTL)
        return {"status": "失败", "msg": public_message}

    except Exception as e:
        logger.exception("Valuation task %s failed", task_id)
        cache.set(redis_key, json.dumps({
            "user_id": user_id,
            "status": "失败",
            "msg": "系统内部错误，请稍后重试。",
            "data": None
        }), VALUATION_TASK_TTL)
        return {"status": "失败", "msg": "系统内部错误，请稍后重试。"}

async def _background_valuation_async(task_id: str, user_id: str, user_desc: str, valid_image_paths: list):
    """
    异步入口：同步执行 AI 估价，完成后通过 WebSocket 推送结果。
    由 background_worker 通过 asyncio.run() 调用，自动获得独立事件循环。
    """
    # AI 计算本身是同步的，直接调用即可（已经在独立线程中了）
    result = _run_valuation_sync(task_id, user_id, user_desc, valid_image_paths)

    # 通过 WebSocket 推送结果给用户（push_valuation_result 是 async 函数）
    from .consumers import push_valuation_result

    if user_id.startswith("guest_"):
        return

    if result.get("status") == "成功":
        await push_valuation_result(user_id, {
            "type": "valuation_result",
            "task_id": task_id,
            "status": "成功",
            "msg": "AI 估价成功！",
            "data": result["data"]
        })
    else:
        await push_valuation_result(user_id, {
            "type": "valuation_result",
            "task_id": task_id,
            "status": "失败",
            "msg": result.get("msg", "估价失败"),
            "data": None
        })

def _background_worker(task_id: str, user_id: str, user_desc: str, valid_image_paths: list):
    """
    同步包装函数：在后台线程中执行，asyncio.run() 自动创建独立事件循环。
    """
    try:
        asyncio.run(
            _background_valuation_async(task_id, user_id, user_desc, valid_image_paths)
        )
    except Exception as e:
        logger.exception("Valuation background worker %s failed", task_id)


class AIEvaluationView(APIView):
    """
    AI智能估价 — 异步提交接口

    HTTP POST 瞬间返回 task_id，后台 threading.Thread 执行 AI 计算，
    完成后通过 WebSocket 推送结果 + 更新 Redis 状态。
    """
    permission_classes = [AllowAny]

    def post(self, request):
        owner = _get_request_owner(request)
        if not owner:
            return Response({"code": 400, "msg": "缺少游客标识，请刷新页面后重试", "data": None}, status=400)

        user_desc = request.data.get('user_desc', '').strip()

        if hasattr(request.data, 'getlist'):
            images_input = request.data.getlist('image_paths')
        else:
            images_input = request.data.get('image_paths', [])

        if not isinstance(images_input, list):
            images_input = [images_input]

        valid_image_paths = []

        for item in images_input:
            if isinstance(item, str) and item.strip():
                if default_storage.exists(item):
                    abs_path = default_storage.path(item)
                    if os.path.isfile(abs_path):
                        valid_image_paths.append(abs_path)

            elif hasattr(item, 'read'):
                ext = item.name.split('.')[-1] if hasattr(item, 'name') and '.' in item.name else 'jpg'
                temp_file_name = f"temp/{uuid.uuid4().hex}.{ext}"
                saved_path = default_storage.save(temp_file_name, item)
                valid_image_paths.append(default_storage.path(saved_path))

        if not valid_image_paths:
            return Response({"code": 400, "msg": "请至少上传一张有效的设备图片！", "data": None}, status=400)

        # 生成 task_id 并写入 Redis 初始状态
        if owner.startswith("guest_"):
            usage_key = f"valuation:guest-used:{owner}"
            if not cache.add(usage_key, "1", GUEST_VALUATION_TTL):
                return Response({"code": 403, "msg": "游客体验次数已用完，请登录后继续估价", "data": None}, status=403)

        task_id = uuid.uuid4().hex
        user_id = owner
        redis_key = _build_redis_key(task_id)

        cache.set(redis_key, json.dumps({
            "user_id": user_id,
            "status": "计算中",
            "msg": "AI 正在深度分析中...",
            "data": None
        }), VALUATION_TASK_TTL)

        # 启动后台线程执行 AI 估价（不阻塞当前 HTTP 请求）
        threading.Thread(
            target=_background_worker,
            args=(task_id, user_id, user_desc, valid_image_paths),
            daemon=True
        ).start()

        # 瞬间返回 task_id
        return Response({
            "code": 200,
            "msg": "估价任务已提交，请等待结果推送。",
            "data": {"task_id": task_id}
        })


class AIEvaluationResultView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, task_id):
        cached_result = cache.get(_build_redis_key(task_id))
        if not cached_result:
            return Response({"code": 404, "msg": "估价任务不存在或已过期", "data": None}, status=404)

        result = json.loads(cached_result)
        if str(result.get("user_id")) not in _get_request_owners(request):
            return Response({"code": 403, "msg": "无权查看该估价任务", "data": None}, status=403)

        return Response({
            "code": 200,
            "msg": result.get("msg", "获取估价任务成功"),
            "data": {
                "task_id": task_id,
                "status": result.get("status"),
                "result": result.get("data"),
            },
        })


class GoodsCreateView(APIView):
    """
    二手商品发布接口
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GoodsSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "code": 400,
                "msg": "参数填写有误，请检查！",
                "errors": serializer.errors
            }, status=400)
        
        # 强制进入审核中，审核通过后才允许进入交易广场
        serializer.save(seller=request.user, status=GoodsStatusChoices.PENDING_REVIEW, audit_reason="")

        return Response({
            "code": 200,
            "msg": "商品已提交审核，通过后将自动上架！",
            "data": serializer.data
        })
class GoodsDraftView(APIView):
    """
    保存商品草稿接口
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 🌟 核心拦截：检查当前用户的草稿数量是否已达上限 (10个)
        draft_count = Goods.objects.filter(seller=request.user, status=0).count()
        if draft_count >= 10:
            return Response({
                "code": 403,
                "msg": "草稿箱已满，最多只能保存 10 个草稿，请先清理",
                "data": None
            }, status=403)

        # 允许某些字段为空
        data = request.data.copy()
        data['status'] = 0 # 强制设为草稿状态
        
        serializer = GoodsSerializer(data=data)

        if not serializer.is_valid():
            return Response({
                "code": 400,
                "msg": "草稿数据格式有误！",
                "errors": serializer.errors
            }, status=400)
            
        serializer.save(seller=request.user)

        return Response({
            "code": 200,
            "msg": "草稿保存成功！",
            "data": serializer.data
        })
class CategoryListView(APIView):
    """
    获取商品大类及动态属性字典 (前端初始化拉取存入 Pinia)
    """
    permission_classes = [AllowAny]

    def get(self, request):
        categories = Category.objects.all().order_by('sort')
        serializer = CategorySerializer(categories, many=True)
        return Response({
            "code": 200,
            "msg": "获取分类字典成功",
            "data": serializer.data
        })
class GoodsDetailView(APIView):
    """获取商品详情"""
    permission_classes = [AllowAny]  # 根据你的需求调整权限

    def get(self, request, pk):
        # 查找指定的商品记录
        goods = get_object_or_404(Goods, pk=pk)

        # 增加浏览量 (可选功能)
        goods.views += 1
        goods.save(update_fields=['views'])

        serializer = GoodsSerializer(goods,context={'request': request})
        return Response({
            "code": 200,
            "msg": "获取商品详情成功",
            "data": serializer.data
        })
class GoodsListView(APIView):
    """
    商品大厅展示与高级动态筛选接口
    """
    permission_classes = [AllowAny]

    def get(self, request):
        # 1. 基础查询：只看在售中(status=1)
        queryset = Goods.objects.filter(status=1).select_related('category', 'seller').prefetch_related('images')

        # 🌟 修改 1：新增按卖家 ID 筛选（用于展示“Ta的主页/Ta的闲置”）
        seller_id = request.query_params.get('seller_id')
        if seller_id:
            queryset = queryset.filter(seller_id=seller_id)

        category_id = request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        keyword = request.query_params.get('keyword')
        if keyword:
            queryset = queryset.filter(title__icontains=keyword)

        # 动态属性筛选：前端以 attr_ 前缀传递属性参数，去掉前缀后匹配 JSONField
        for key, value in request.query_params.items():
            if key.startswith('attr_') and value:
                attr_name = key[5:]  # 去掉 attr_ 前缀
                queryset = queryset.filter(**{f"attributes__{attr_name}": value})

        queryset = queryset.order_by('-created_at')

        serializer = GoodsSerializer(queryset, many=True, context={'request': request})

        return Response({
            "code": 200,
            "msg": "获取商品列表成功",
            "data": serializer.data
        })
class MyGoodsListView(APIView):
    """
    获取我发布的商品
    支持按状态筛选：全部、在售中、已下架、已售出等
    """
    # 🌟 必须登录才能看自己的！
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Goods.objects.filter(seller=request.user).select_related('category').prefetch_related('images')

        # 2. 按状态筛选 (前端传什么 status 就查什么)
        # 注意这里用 is not None 判断，因为如果是草稿的话 status 可能是 0
        status_param = request.query_params.get('status')
        if status_param is not None and status_param.strip() != '':
            queryset = queryset.filter(status=status_param)

        keyword = request.query_params.get('keyword')
        if keyword:
            queryset = queryset.filter(title__icontains=keyword)

        # 4. 排序 (最新的排前面)
        queryset = queryset.order_by('-created_at')

        # 5. 序列化并返回
        serializer = GoodsSerializer(queryset, many=True, context={'request': request})

        return Response({
            "code": 200,
            "msg": "获取我的商品成功",
            "data": serializer.data
        })
class ImageUploadView(APIView):
    """
    商品临时图片上传接口（免登录，带自动销毁机制）
    """
    # 允许免登录访问
    permission_classes = [AllowAny]

    def post(self, request):
        owner = _get_request_owner(request)
        if not owner:
            return Response({"code": 400, "msg": "缺少游客标识，请刷新页面后重试"}, status=400)
        if owner.startswith("guest_") and cache.get(f"valuation:guest-used:{owner}"):
            return Response({"code": 403, "msg": "游客体验次数已用完，请登录后继续使用"}, status=403)

        # 清硬盘接口
        clean_expired_temp_files()

        # 拿文件并校验
        file_obj = request.FILES.get('image')
        if not file_obj:
            return Response({"code": 400, "msg": "没有接收到图片文件，请检查参数"}, status=400)

        # 限制文件大小（最大 5MB）
        if file_obj.size > 5 * 1024 * 1024:
            return Response({"code": 400, "msg": "老板，图片太大了，不能超过 5MB 哦！"}, status=400)

        # 限制文件格式
        ext = os.path.splitext(file_obj.name)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
            return Response({"code": 400, "msg": "仅支持 JPG/PNG/WEBP 格式的图片！"}, status=400)

        # 生成绝对不重复的新文件名并保存
        new_filename = f"{uuid.uuid4().hex}{ext}"
        save_path = os.path.join('temp', new_filename)
        actual_path = default_storage.save(save_path, file_obj)
        return Response({
            "code": 200,
            "msg": "上传成功！",
            "data": {
                "file_path": actual_path,
                "url": f"/media/{actual_path}"
            }
        })
class ToggleLikeView(APIView):
    """
    收藏/取消收藏 切换接口
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        goods_id = request.data.get('goods_id')
        if not goods_id:
            return Response({"code": 400, "msg": "缺失商品ID参数"}, status=400)

        goods = get_object_or_404(Goods, id=goods_id)

        like_obj, created = GoodsLike.objects.get_or_create(
            user=request.user,
            goods=goods
        )

        if created:
            return Response({"code": 200, "msg": "收藏成功", "data": {"is_like": True}})
        else:
            like_obj.delete()
            return Response({"code": 200, "msg": "已取消收藏", "data": {"is_like": False}})

class MyLikeListView(APIView):
    """
    获取我的收藏列表
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Goods.objects.filter(
            like_by__user=request.user
        ).order_by('-like_by__created_at')

        serializer = GoodsSerializer(queryset, many=True, context={'request': request})

        return Response({
            "code": 200,
            "msg": "获取收藏列表成功",
            "data": serializer.data
        })

class GoodsStatusUpdateView(APIView):
    """
    商品上下架状态切换接口
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        goods_id = request.data.get('goods_id')
        action = request.data.get('action')

        if not goods_id or action not in ['delist', 'publish']:
            return Response({"code": 400, "msg": "参数错误"}, status=400)

        goods = get_object_or_404(Goods, id=goods_id)

        if goods.seller != request.user:
            return Response({"code": 403, "msg": "非本人商品，无权操作！"}, status=403)

        # 执行业务逻辑
        if action == 'delist':
            if goods.status == 3:
                return Response({"code": 400, "msg": "商品已经是下架状态"})
            goods.status = 3
            goods.save()
            return Response({"code": 200, "msg": "商品已成功下架"})

        elif action == 'publish':
            if goods.status == 1:
                return Response({"code": 400, "msg": "商品已经在售中"})
            goods.status = GoodsStatusChoices.PENDING_REVIEW
            goods.audit_reason = ""
            goods.save(update_fields=["status", "audit_reason", "updated_at"])
            return Response({"code": 200, "msg": "商品已重新提交审核，审核通过后将自动上架"})

class GoodsDeleteView(APIView):
    """
    商品删除接口
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        goods_id = request.data.get('goods_id')
        if not goods_id:
            return Response({"code": 400, "msg": "缺失商品ID参数"}, status=400)

        goods = get_object_or_404(Goods, id=goods_id)

        # 🛡️ 铁血防线 1：绝对不允许删除别人的商品！
        if goods.seller != request.user:
            return Response({"code": 403, "msg": "非本人商品，无权删除！"}, status=403)

        if goods.status == 2:
            return Response({"code": 400, "msg": "已售出的商品无法删除，请保留作为交易凭证！"}, status=400)

        goods.delete()

        return Response({
            "code": 200,
            "msg": "商品已永久删除"
        })
