"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

# 必须先调用 get_asgi_application()，确保 Django 初始化完成后再导入 channels 相关模块
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from apps.chats.channels_middleware import JWTAuthMiddleware
from apps.chats.routing import websocket_urlpatterns as chat_ws_patterns
from apps.goods.routing import websocket_urlpatterns as valuation_ws_patterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JWTAuthMiddleware(
        URLRouter(chat_ws_patterns + valuation_ws_patterns)
    ),
})
