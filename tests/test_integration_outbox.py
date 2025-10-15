# tests/test_integration_outbox.py
import os
import asyncio
import pytest
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer
from app.infra.db.repo_async import create_tables, AsyncTaskRepository, engine
from app.domain.services_async import TaskServiceAsync
from aioredis import from_url
import time


@pytest.mark.asyncio
async def test_outbox_flow():
    with PostgresContainer("postgres:15") as pg, RedisContainer("redis:7") as rd:
        # set env vars for test
        db_url = pg.get_connection_url().replace(
            "postgresql://", "postgresql+asyncpg://"
        )
        os.environ["DATABASE_URL"] = db_url
        redis_url = f"redis://{rd.get_container_host_ip()}:{rd.get_exposed_port(6379)}"
        os.environ["REDIS_URL"] = redis_url
        os.environ["REDIS_STREAM"] = "tasks:events"

        # reinitialize engine
        # create tables
        await create_tables()

        repo = AsyncTaskRepository()
        service = TaskServiceAsync(repo)

        # create a task => creates outbox row
        task = await service.create_task("itest", {"a": 1})
        assert task.name == "itest"

        # run flusher briefly
        from app.infra.outbox.flusher import OutboxFlusher

        fl = OutboxFlusher(repo, redis_url=redis_url, poll_interval=0.2)
        fl_task = asyncio.create_task(fl.run_loop())
        await asyncio.sleep(1.0)  # wait for flusher to pick up
        # check redis stream
        r = await from_url(redis_url)
        resp = await r.xrevrange("tasks:events", count=10)
        await r.close()
        # cancel flusher
        fl_task.cancel()
        try:
            await fl_task
        except asyncio.CancelledError:
            pass
        assert len(resp) >= 1
