import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_client import make_asgi_app

from app.api.v1 import samurai_commands, samurai_queries
from app.infra.db.repo_async import create_tables, AsyncTaskRepository
from app.infra.outbox.flusher import OutboxFlusher
from app.workers.flusher_entrypoint import run as run_flusher
from app.settings import settings

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger("samurai")


# shared singletons
repo = AsyncTaskRepository()
flusher = OutboxFlusher(
    repo,
    redis_url=settings.redis_url,
    poll_interval=settings.outbox_poll_interval,
)


@asynccontextmanager
async def lifespan(application: FastAPI()):
    """Handles startup and shutdown using FastAPI lifespan."""
    logger.info("startup: creating tables")
    await create_tables()

    # start background task
    # flusher_task = asyncio.create_task(flusher.run_loop())
    flusher_task = asyncio.create_task(run_flusher())
    application.state._flusher_task = flusher_task
    logger.info("flusher started")

    # yield control to the app runtime
    try:
        yield
    finally:
        logger.info("shutdown: stopping flusher")
        await flusher.stop()
        flusher_task.cancel()
        try:
            await flusher_task
        except asyncio.CancelledError:
            pass
        logger.info("shutdown complete")


app = FastAPI(
    title="Samurai Tasks (with Outbox)",
    description="Backend for frontend aka. API Gateway!",
    version="0.0.1",
    docs_url="/docs/" if settings.app_debug else None,
    redoc_url="/redoc/" if settings.app_debug else None,
    lifespan=lifespan,
)


# health check
@app.get("/health")
async def health():
    return {"status": "ok"}


# mount prometheus metrics at /metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# include routes
app.include_router(samurai_commands.router)
app.include_router(samurai_queries.router)
