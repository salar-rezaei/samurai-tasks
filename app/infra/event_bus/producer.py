# app/infra/event_bus/producer.py
"""
Redis Stream producer wrapper.
(در این پروژه از Flusher برای انتشار outbox استفاده کردم؛ ولی producer جدا مفید است برای تست و reuse)
"""
import json
from redis.asyncio import from_url
from app.settings import settings


class RedisStreamProducer:
    def __init__(self, redis_url: str = None):
        self._redis_url = redis_url or settings.redis_url
        self._client = None

    async def client(self):
        if not self._client:
            self._client = await from_url(self._redis_url)
        return self._client

    async def publish(self, stream: str, event_type: str, payload: dict) -> str:
        r = await self.client()
        entry = {"type": event_type, "payload": json.dumps(payload)}
        stream_id = await r.xadd(stream, entry)
        return str(stream_id)

    async def close(self):
        if self._client:
            await self._client.close()
            self._client = None
