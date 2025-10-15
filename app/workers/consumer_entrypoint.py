# app/workers/consumer_entrypoint.py
import asyncio
import logging
from prometheus_client import Counter, start_http_server
from sqlalchemy import update

from app.infra.db.repo_async import AsyncTaskRepository
from app.infra.event_bus import consumer as consumer_module
from app.infra.redis.lock import RedisLock
from app.settings import settings
from app.infra.db.sqlalchemy_models import TaskORM
from app.infra.db.repo_async import AsyncSessionLocal

EVENTS_CONSUMED = Counter("samurai_events_consumed_total", "Total consumed events")
EVENTS_PROCESS_ERRORS = Counter(
    "samurai_events_process_errors_total", "Errors processing events"
)

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger("worker")

task_repo = AsyncTaskRepository()


async def handle(event_type: str, task_id: str, data: dict, redis):
    lock = RedisLock(redis, f"task-lock:{data.get('task_id')}")

    task_id = task_id or data.get("task_id")
    if not task_id:
        logger.warning("No task_id in event, skipping")
        return

    try:
        logger.info(
            "handle event_type=%s task_id=%s data=%s", event_type, task_id, data
        )
        EVENTS_CONSUMED.inc()
        # task process simulator
        await asyncio.sleep(0.4)

        # update DB
        async with AsyncSessionLocal() as session:
            async with session.begin():
                stmt = (
                    update(TaskORM)
                    .where(TaskORM.id == task_id)
                    .values(state="processed")
                )
                await session.execute(stmt)

        logger.info(f"Task {task_id} marked as processed by consumer 1.")

    except Exception as e:
        EVENTS_PROCESS_ERRORS.inc()
        logger.exception(f"Error processing task by consumer 1 {task_id}: {e}")
    finally:
        await lock.release()


async def run():

    start_http_server(settings.consumer_port)

    consumer_declare = consumer_module.RedisStreamConsumer(
        stream=settings.stream_name,
        group=settings.consumer_group,
        consumer_name=settings.consumer_name,
    )
    redis = await consumer_declare.get_client()

    logger.info(
        "Consumer started, listening to Redis stream '%s'...", settings.stream_name
    )

    try:

        async def wrapped_handler(event_type, task_id, data):
            await handle(event_type, task_id, data, redis)

        await consumer_declare.run(wrapped_handler, read_count=5)
    except asyncio.CancelledError:
        logger.info("Consumer stopped by user")
    finally:
        await consumer_declare.stop()


if __name__ == "__main__":
    asyncio.run(run())
