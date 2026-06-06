from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import ChatSession, ChatMessage, SystemAnnouncement
from .serializers import ChatSessionSerializer, ChatMessageSerializer, SystemAnnouncementSerializer
from django.shortcuts import get_object_or_404


def get_user_session_or_403(session_id, user):
    session = get_object_or_404(ChatSession, id=session_id)
    if user != session.initiator and user != session.receiver:
        return None
    return session


class SessionViewSet(APIView):
    """
    点击‘联系卖家’：获取或创建会话
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        goods_id = request.data.get('goods_id')
        receiver_id = request.data.get('receiver_id')
        initiator = request.user

        if not goods_id or not receiver_id:
            return Response({"code": 400, "msg": "缺少商品或接收方参数"}, status=400)

        if str(receiver_id) == str(initiator.id):
            return Response({"code": 400, "msg": "不能和自己创建会话"}, status=400)

        # 修复：无论谁是发起人，只要俩人商品一样，就是同一个会话
        session = ChatSession.objects.filter(goods_id=goods_id).filter(
            Q(initiator=initiator, receiver_id=receiver_id) |
            Q(initiator_id=receiver_id, receiver=initiator)
        ).first()

        if not session:
            session = ChatSession.objects.create(
                goods_id=goods_id,
                initiator=initiator,
                receiver_id=receiver_id,
                last_message_at=timezone.now()
            )

        return Response({"code": 200, "data": {"session_id": session.id}})

    def get(self, request):
        """我的消息列表"""
        sessions = ChatSession.objects.filter(
            Q(initiator=request.user) | Q(receiver=request.user)
        ).select_related(
            'goods', 'initiator', 'receiver'
        ).prefetch_related(
            'goods__images'
        ).order_by('-last_message_at')

        serializer = ChatSessionSerializer(sessions, many=True, context={'request': request})
        return Response({"code": 200, "data": serializer.data})

class SendMessageView(APIView):
    """
    发消息接口
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session_id = request.data.get('session_id')
        content = request.data.get('content', '').strip()

        session = get_user_session_or_403(session_id, request.user)
        if not session:
            return Response({"code": 403, "msg": "无权操作此会话"}, status=403)

        if session.status != 0:
            return Response({"code": 403, "msg": "当前会话不可发送消息"}, status=403)

        if not content:
            return Response({"code": 400, "msg": "消息内容不能为空"}, status=400)

        if len(content) > 500:
            return Response({"code": 400, "msg": "消息内容不能超过 500 字"}, status=400)

        # 创建消息
        msg = ChatMessage.objects.create(
            session=session,
            sender=request.user,
            content=content,
            content_type='text'
        )

        # 更新会话表的最后消息和未读数
        session.last_message = content
        session.last_message_at = timezone.now()  # 手动更新最后消息时间
        if request.user == session.initiator:
            session.unread_receiver += 1  # 我是买家发消息，卖家未读+1
        else:
            session.unread_initiator += 1  # 我是卖家发消息，买家未读+1
        session.save()

        # 返回完整的消息对象（含嵌套 sender 信息）
        serializer = ChatMessageSerializer(msg)
        message_data = serializer.data

        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"chats_{session.id}",
                {
                    "type": "chats.message",
                    "data": message_data,
                }
            )

        return Response({"code": 200, "msg": "发送成功", "data": message_data})
class MessageListView(APIView):
    """
    get：获取会话列表
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        session = get_user_session_or_403(session_id, request.user)
        if not session:
            return Response({"code": 403, "msg": "无权查看此会话"}, status=403)

        messages = ChatMessage.objects.filter(session=session).order_by('created_at')
        serializer = ChatMessageSerializer(messages, many=True)
        return Response({"code": 200, "data": serializer.data})

class MarkReadView(APIView):
    """
    post：消息已读处理
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        """将指定会话中，对方发给我的消息标记为已读"""
        session = get_user_session_or_403(session_id, request.user)
        user = request.user

        if not session:
            return Response({"code": 403, "msg": "无权操作此会话"}, status=403)

        # 清零会话表里的未读红点数
        if user == session.initiator:
            session.unread_initiator = 0  # 如果我是买家，清空买家的未读数
        else:
            session.unread_receiver = 0   # 如果我是卖家，清空卖家的未读数
        session.save()

        # 批量更新消息表
        # 条件：这个会话下 + 不是我发的 + 目前还是未读的
        updated_count = ChatMessage.objects.filter(
            session=session,
            is_read=False
        ).exclude(
            sender=user  #排除掉自己发的消息
        ).update(is_read=True)

        return Response({
            "code": 200,
            "msg": "已读标记成功",
            "data": {"updated_count": updated_count} #顺便返回一下清掉了几条未读
        })


class SystemAnnouncementListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notices = SystemAnnouncement.objects.filter(is_active=True).order_by("-created_at")[:50]
        serializer = SystemAnnouncementSerializer(notices, many=True)
        return Response({"code": 200, "msg": "获取系统公告成功", "data": serializer.data})

