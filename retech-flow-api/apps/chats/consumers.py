"""
Django Channels WebSocket Consumer — 聊天消息收发

连接地址：ws://host/ws/chats/<session_id>/?token=<jwt>
消息格式（客户端发送）：{"message": "文本内容"}
消息格式（服务端广播）：与 ChatMessageSerializer 一致的完整消息对象
"""

import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone


class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        """
        WebSocket 握手：鉴权 + 加入房间组
        """
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'chats_{self.session_id}'
        self.user = self.scope.get('user', AnonymousUser())

        # 未登录则拒绝连接
        if not self.user or self.user.is_anonymous:
            await self.close()
            return

        # 校验用户是否是该会话的参与者
        is_participant = await self.check_participant()
        if not is_participant:
            await self.close()
            return

        # 加入 channel layer 房间组
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # 进入聊天窗口即标记已读，并通知对方
        await self.mark_session_read()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'messages.read',
                'reader_id': self.user.id,
            }
        )

    async def disconnect(self, close_code):
        """
        断开连接：离开房间组
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive_json(self, content, **kwargs):
        """
        收到客户端消息：保存到数据库 + 广播给房间内所有连接
        """
        message_text = content.get('message', '').strip()
        if not message_text:
            return

        # 保存消息到数据库，返回序列化后的消息数据
        msg_data = await self.save_message(message_text)
        if msg_data is None:
            return

        # 广播消息给房间组内所有连接（包括自己）
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chats.message',
                'data': msg_data,
            }
        )

    async def chats_message(self, event):
        """
        处理房间组广播事件：将消息推送给 WebSocket 客户端
        """
        msg_data = event['data']
        sender_id = msg_data.get('sender', {}).get('id')

        # 如果这条消息不是我发的（即我是接收方），自动标记已读并通知对方
        if sender_id and sender_id != self.user.id:
            await self.mark_session_read()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'messages.read',
                    'reader_id': self.user.id,
                }
            )

        await self.send_json({
            'type': 'chats.message',
            'data': msg_data,
        })

    async def messages_read(self, event):
        """
        处理已读通知事件：通知发送方消息已被对方阅读
        """
        await self.send_json({
            'type': 'messages.read',
            'reader_id': event['reader_id'],
        })

    # ========== 数据库操作（同步→异步） ==========

    @database_sync_to_async
    def check_participant(self):
        """检查当前用户是否是该会话的参与者"""
        from .models import ChatSession
        try:
            session = ChatSession.objects.get(id=self.session_id)
            return self.user == session.initiator or self.user == session.receiver
        except ChatSession.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, text):
        """
        保存消息到数据库，并更新会话的 last_message / last_message_at / 未读数。
        返回与 ChatMessageSerializer 格式一致的字典。
        """
        from .models import ChatSession, ChatMessage
        try:
            session = ChatSession.objects.get(id=self.session_id)
        except ChatSession.DoesNotExist:
            return None

        # 创建消息记录
        msg = ChatMessage.objects.create(
            session=session,
            sender=self.user,
            content=text,
            content_type='text',
        )

        # 更新会话摘要
        session.last_message = text
        session.last_message_at = timezone.now()
        if self.user == session.initiator:
            session.unread_receiver += 1
        else:
            session.unread_initiator += 1
        session.save()

        # 构造与 ChatMessageSerializer 一致的返回数据
        return {
            'id': msg.id,
            'session': session.id,
            'sender': {
                'id': self.user.id,
                'nickname': self.user.nickname,
                'avatar': str(self.user.avatar) if self.user.avatar else None,
            },
            'content_type': msg.content_type,
            'content': msg.content,
            'send_status': msg.send_status,
            'is_read': msg.is_read,
            'created_at': msg.created_at.isoformat(),
        }

    @database_sync_to_async
    def mark_session_read(self):
        """进入聊天窗口时，将对方发给我的消息标记为已读"""
        from .models import ChatSession, ChatMessage
        try:
            session = ChatSession.objects.get(id=self.session_id)
        except ChatSession.DoesNotExist:
            return

        # 清零会话未读数
        if self.user == session.initiator:
            session.unread_initiator = 0
        else:
            session.unread_receiver = 0
        session.save()

        # 批量标记消息已读
        ChatMessage.objects.filter(
            session=session,
            is_read=False
        ).exclude(
            sender=self.user
        ).update(is_read=True)
