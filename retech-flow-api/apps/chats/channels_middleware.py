"""
Django Channels WebSocket JWT 鉴权中间件

WebSocket 不支持自定义 Header，因此从 URL query_params 中提取 token 字段：
    ws://host/ws/chats/<session_id>/?token=<jwt_access_token>

校验通过后将 User 对象存入 scope['user']，供 Consumer 使用。
"""

from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken


@database_sync_to_async
def get_user_from_token(token_str):
    """
    手动解析 JWT access token，返回对应的 User 对象。
    失败则返回 AnonymousUser。
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # 解码并验证 access token（SimpleJWT 会自动检查签名和过期时间）
        access_token = AccessToken(token_str)
        user_id = access_token['user_id']  # ShortUUID 字符串
        user = User.objects.get(id=user_id)
        return user
    except Exception:
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """
    从 WebSocket 连接的 query string 中提取 token，完成用户鉴权。
    """

    async def __call__(self, scope, receive, send):
        # 解析 query string: ?token=xxx
        query_string = scope.get('query_string', b'').decode('utf-8')
        query_params = parse_qs(query_string)
        token_list = query_params.get('token', [])

        if token_list:
            scope['user'] = await get_user_from_token(token_list[0])
        else:
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)
