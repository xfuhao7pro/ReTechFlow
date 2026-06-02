"""
goods app — WebSocket 路由

连接地址：ws://127.0.0.1:8000/ws/valuation/?token=xxx
"""

from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/valuation/', consumers.ValuationConsumer.as_asgi()),
]
