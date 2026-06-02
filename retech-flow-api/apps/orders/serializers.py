from rest_framework import serializers
from .models import Order


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
    buyer_name = serializers.CharField(source='buyer.nickname', read_only=True)

    class Meta:
        model = Order
        # 选出前端展示订单列表和详情时需要的字段
        fields = [
            'order_id', 'amount', 'status', 'status_text',
            'goods_id', 'goods_title', 'goods_price', 'goods_image', 
            'seller_name', 'buyer_name',
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