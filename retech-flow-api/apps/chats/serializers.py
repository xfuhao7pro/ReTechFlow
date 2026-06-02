from rest_framework import serializers
from .models import ChatSession, ChatMessage
from apps.users.models import PlatformUser  # 确保路径正确
from apps.goods.models import Goods, GoodsImage


class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformUser
        fields = ['id', 'nickname', 'avatar']


class GoodsSimpleSerializer(serializers.ModelSerializer):
    """会话列表中展示的商品摘要信息（含封面图）"""
    cover = serializers.SerializerMethodField()

    class Meta:
        model = Goods
        fields = ['id', 'title', 'cover']

    def get_cover(self, obj):
        # 优先取 is_cover=True 的主图，否则取第一张图
        cover_img = obj.images.filter(is_cover=True).first()
        if not cover_img:
            cover_img = obj.images.first()
        if cover_img and cover_img.image:
            return str(cover_img.image)
        return None


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = UserSimpleSerializer(read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'session', 'sender', 'content_type', 'content', 'send_status', 'is_read', 'created_at']


class ChatSessionSerializer(serializers.ModelSerializer):
    other_user = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    goods = GoodsSimpleSerializer(read_only=True)

    class Meta:
        model = ChatSession
        fields = [
            'id', 'goods', 'last_message', 'last_message_at',
            'updated_at', 'unread_count', 'other_user'
        ]

    def get_unread_count(self, obj):
        request_user = self.context['request'].user
        # 如果我是发起人，我的未读数存在unread_initiator里
        if obj.initiator == request_user:
            return obj.unread_initiator
        # 如果我是接收人，我的未读数存在unread_receiver里
        return obj.unread_receiver

    def get_other_user(self, obj):
        request_user = self.context['request'].user
        # 如果我是发起者，对方就是接收者；反之亦然
        target_user = obj.receiver if obj.initiator == request_user else obj.initiator
        return UserSimpleSerializer(target_user).data