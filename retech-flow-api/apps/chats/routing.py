"""
Django Channels WebSocket 路由

连接地址示例：ws://127.0.0.1:8000/ws/chats/<session_id>/?token=xxx
"""

from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/chats/<str:session_id>/', consumers.ChatConsumer.as_asgi()),
]
