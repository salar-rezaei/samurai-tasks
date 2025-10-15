# app/infra/event_bus/consumer.py
import asyncio
import json
from typing import Callable, Awaitable
from redis.asyncio import from_url, Redis
from app.settings import settings
import logging

logger = logging.getLogger("event.consumer")


class RedisStreamConsumer:
    def __init__(
        self,
        stream: str,
        group: str = "samurai-workers",
        consumer_name: str = "consumer-1",
    ):
        self.stream = stream
        self.group = group
        self.consumer_name = consumer_name
        self.redis_url = settings.redis_url
        self._client: Redis | None = None
        self._stopped = False

    async def _get_client(self):
        if not self._client:
            self._client = await from_url(self.redis_url)
        return self._client

    async def get_client(self):
        return await self._get_client()

    async def ensure_group(self):
        r = await self._get_client()
        try:
            await r.xgroup_create(self.stream, self.group, id="0", mkstream=True)
        except Exception as e:
            logger.debug("group create: %s", e)

    async def run(
        self, handler: Callable[[str, str, dict], Awaitable[None]], read_count: int = 1
    ):
        r = await self._get_client()
        await self.ensure_group()
        while not self._stopped:
            try:
                resp = await r.xreadgroup(
                    self.group,
                    self.consumer_name,
                    streams={self.stream: ">"},
                    count=read_count,
                )
                if not resp:
                    await asyncio.sleep(0.2)
                    continue
                for _, messages in resp:
                    for msg_id, raw in messages:
                        try:
                            event_type = raw.get(b"type").decode()
                            task_id = (
                                raw.get(b"task_id").decode()
                                if raw.get(b"task_id")
                                else ""
                            )
                            data = {}
                            raw_payload = raw.get(b"payload")
                            if raw_payload:
                                try:
                                    data = json.loads(raw_payload.decode())
                                except Exception:
                                    data = {}
                            await handler(event_type, task_id, data)
                            await r.xack(self.stream, self.group, msg_id)
                        except Exception as e:
                            logger.exception(
                                "processing message %s failed: %s", msg_id, e
                            )
            except Exception as e:
                logger.exception("consumer loop error: %s", e)
                await asyncio.sleep(1.0)

    async def stop(self):
        self._stopped = True
        if self._client:
            await self._client.close()
            self._client = None
