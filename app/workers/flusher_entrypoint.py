# app/workers/flusher_entrypoint.py
import asyncio
import logging
from app.infra.db.repo_async import AsyncTaskRepository
from app.infra.outbox.flusher import OutboxFlusher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("flusher")


async def run():
    repo = AsyncTaskRepository()
    flusher = OutboxFlusher(repo)
    try:
        await flusher.run_loop()
    except asyncio.CancelledError:
        logger.info("Flusher stopped by user")
    finally:
        await flusher.stop()


if __name__ == "__main__":
    asyncio.run(run())
