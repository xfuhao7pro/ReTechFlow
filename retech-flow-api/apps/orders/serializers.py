from rest_framework import serializers
from .models import Order, OrderAppeal


class OrderSerializer(serializers.ModelSerializer):
    """
    订单通用序列化器
    """

    status_text = serializers.CharField(source='get_status_display', read_only=True)

    # 嵌套读取外键数据：把前端需要的商品信息直接拼好，省得前端再去查一次
    goods_id = serializers.CharField(source='goods.id', read_only=True)
    goods_title = serializers.SerializerMethodField()
    goods_price = serializers.SerializerMethodField()
    goods_image = serializers.SerializerMethodField()

    # 3. 卖家和买家信息展示
    seller_name = serializers.CharField(source='seller.nickname', read_only=True)
    seller_avatar = serializers.CharField(source='seller.avatar', read_only=True)
    buyer_name = serializers.CharField(source='buyer.nickname', read_only=True)
    buyer_avatar = serializers.CharField(source='buyer.avatar', read_only=True)

    class Meta:
        model = Order
        # 选出前端展示订单列表和详情时需要的字段
        fields = [
            'order_id', 'amount', 'status', 'status_text',
            'goods_id', 'goods_title', 'goods_price', 'goods_image', 
            'seller_name', 'seller_avatar', 'buyer_name', 'buyer_avatar',
            'receiver_name', 'receiver_phone', 'receiver_address',
            'tracking_number', 'created_at', 'pay_time', 'consign_time'
        ]
        
    def get_goods_title(self, obj):
        return obj.goods.title if obj.goods else obj.snapshot_content
        
    def get_goods_price(self, obj):
        return obj.goods.price if obj.goods else obj.amount
        
    def get_goods_image(self, obj):
        if obj.goods:
            cover = obj.goods.images.filter(is_cover=True).first()
            if not cover:
                cover = obj.goods.images.first()
            if cover:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(cover.image.url)
                return cover.image.url
        
        # 如果没有 goods（被删除），使用快照
        request = self.context.get('request')
        if request and obj.snapshot_image and not obj.snapshot_image.startswith('http'):
            return request.build_absolute_uri(obj.snapshot_image)
        return obj.snapshot_image


class OrderAppealSerializer(serializers.ModelSerializer):
    order_id = serializers.CharField(source="order.order_id", read_only=True)
    order_amount = serializers.DecimalField(source="order.amount", max_digits=10, decimal_places=2, read_only=True)
    order_status = serializers.IntegerField(source="order.status", read_only=True)
    order_status_text = serializers.CharField(source="order.get_status_display", read_only=True)
    goods_id = serializers.CharField(source="order.goods.id", read_only=True)
    goods_title = serializers.SerializerMethodField()
    goods_image = serializers.SerializerMethodField()
    buyer_name = serializers.CharField(source="order.buyer.nickname", read_only=True)
    seller_name = serializers.CharField(source="order.seller.nickname", read_only=True)
    applicant_name = serializers.CharField(source="applicant.nickname", read_only=True)
    applicant_role = serializers.SerializerMethodField()
    status_text = serializers.CharField(source="get_status_display", read_only=True)
    result_text = serializers.CharField(source="get_result_display", read_only=True)
    handled_by_name = serializers.CharField(source="handled_by.nickname", read_only=True)

    class Meta:
        model = OrderAppeal
        fields = [
            "id", "order_id", "order_amount", "order_status", "order_status_text",
            "goods_id", "goods_title", "goods_image", "buyer_name", "seller_name",
            "applicant_name", "applicant_role", "issue_type", "description",
            "original_order_status", "status", "status_text", "result", "result_text",
            "admin_remark", "handled_by_name", "created_at", "updated_at", "handled_at",
        ]

    def get_goods_title(self, obj):
        return obj.order.goods.title if obj.order.goods else obj.order.snapshot_content

    def get_goods_image(self, obj):
        if obj.order.goods:
            cover = obj.order.goods.images.filter(is_cover=True).first() or obj.order.goods.images.first()
            if cover:
                request = self.context.get("request")
                if request:
                    return request.build_absolute_uri(cover.image.url)
                return cover.image.url
        request = self.context.get("request")
        if request and obj.order.snapshot_image and not obj.order.snapshot_image.startswith("http"):
            return request.build_absolute_uri(obj.order.snapshot_image)
        return obj.order.snapshot_image

    def get_applicant_role(self, obj):
        if obj.applicant_id == obj.order.buyer_id:
            return "买家"
        if obj.applicant_id == obj.order.seller_id:
            return "卖家"
        return "用户"
