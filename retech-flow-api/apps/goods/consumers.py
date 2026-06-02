import logging

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)


def _valuation_group_name(user_id: str) -> str:
    return f"valuation_user_{user_id}"


class ValuationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user", AnonymousUser())
        if not self.user or self.user.is_anonymous:
            await self.close()
            return

        self.group_name = _valuation_group_name(str(self.user.id))
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        return None

    async def valuation_result(self, event):
        await self.send_json(event["payload"])


async def push_valuation_result(user_id: str, payload: dict):
    channel_layer = get_channel_layer()
    if channel_layer is None:
        logger.error("No channel layer configured; valuation result remains available in cache")
        return

    await channel_layer.group_send(
        _valuation_group_name(user_id),
        {
            "type": "valuation.result",
            "payload": payload,
        },
    )
