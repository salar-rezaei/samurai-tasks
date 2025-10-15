# app/infra/outbox/flusher.py
import asyncio
import json
import uuid
import logging

from redis.asyncio import from_url, Redis
from prometheus_client import Counter, Gauge
from app.infra.db.repo_async import AsyncTaskRepository
from app.settings import settings


logger = logging.getLogger("outbox.flusher")

OUTBOX_PUBLISHED = Counter(
    "samurai_outbox_published_total", "Total outbox events published"
)
OUTBOX_ERRORS = Counter("samurai_outbox_publish_errors_total", "Outbox publish errors")
OUTBOX_PENDING = Gauge("samurai_outbox_pending", "Current pending outbox count")


class OutboxFlusher:
    """
    Flusher در فواصل مشخص، event های Outbox را از دیتابیس خوانده
    و به Redis Stream می‌فرستد.
    """

    def __init__(
        self,
        repo: AsyncTaskRepository,
        redis_url: str | None = None,
        poll_interval: float | None = None,
    ):
        self.repo = repo
        self.redis_url = redis_url or settings.redis_url
        self.poll_interval = poll_interval or settings.outbox_poll_interval
        self._redis: Redis | None = None
        self._running = False

    async def _client(self) -> Redis:
        """Client lazy initializer"""
        if not self._redis:
            self._redis = from_url(self.redis_url)
        return self._redis

    async def run_loop(self):
        """Main flusher loop"""
        self._running = True
        logger.info("Outbox flusher started (poll_interval=%s)", self.poll_interval)

        while self._running:
            try:
                pending = await self.repo.fetch_pending_outbox(limit=50)
                OUTBOX_PENDING.set(len(pending))

                if not pending:
                    await asyncio.sleep(self.poll_interval)
                    continue

                r = await self._client()

                for ev in pending:
                    try:
                        payload = ev.payload or {}
                        # تبدیل UUID و هر object غیر JSON به str
                        for k, v in payload.items():
                            if isinstance(v, uuid.UUID):
                                payload[k] = str(v)
                        entry = {
                            "type": ev.event_type,
                            "payload": json.dumps(payload),
                            "created_at": ev.created_at.isoformat(),
                        }

                        # publish to redis stream
                        stream_id = await r.xadd(ev.stream, entry)
                        await self.repo.mark_outbox_published(
                            ev.id, stream_id=str(stream_id)
                        )
                        OUTBOX_PUBLISHED.inc()
                        logger.info(
                            "Published outbox id=%s to stream=%s id=%s",
                            ev.id,
                            ev.stream,
                            stream_id,
                        )

                    except Exception as exc:
                        OUTBOX_ERRORS.inc()
                        logger.exception(
                            "Failed publishing outbox id=%s: %s", ev.id, exc
                        )

                await asyncio.sleep(0.01)

            except Exception as e:
                logger.exception("Outbox flusher loop error: %s", e)
                await asyncio.sleep(1.0)

    async def stop(self):
        """Stop loop and close redis"""
        self._running = False
        if self._redis:
            await self._redis.aclose()
            self._redis = None
