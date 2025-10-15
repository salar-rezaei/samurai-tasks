# app/infra/db/repo_async.py
from typing import List
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update
from datetime import datetime
from app.settings import settings
from .sqlalchemy_models import Base, TaskORM, EventOutboxORM
from app.domain.models import Task as DomainTask
from app.domain.exceptions import TaskNotFoundError

DATABASE_URL = settings.database_url

# engine و session factory
engine = create_async_engine(DATABASE_URL, future=True, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class AsyncTaskRepository:
    def __init__(self):
        self._session_factory = AsyncSessionLocal

    async def add_task_with_outbox(
        self, domain_task: DomainTask, outbox_event: dict
    ) -> None:
        """
        insert task and outbox record as a atomic transaction
        """
        async with self._session_factory() as session:
            async with session.begin():
                task = TaskORM(
                    id=domain_task.id,
                    name=domain_task.name,
                    payload=domain_task.payload,
                    state=domain_task.state,
                    attempts=domain_task.attempts,
                    last_error=domain_task.last_error,
                )
                session.add(task)

                task_payload = {
                    "task_id": str(domain_task.id),  # <--- تبدیل UUID به str
                    "name": domain_task.name,
                    "payload": domain_task.payload,
                }

                ev = EventOutboxORM(
                    stream=outbox_event["stream"],
                    event_type=outbox_event["event_type"],
                    payload=task_payload,
                )

                session.add(ev)
            # commit happens at exit

    async def get_task(self, task_id) -> DomainTask:
        async with self._session_factory() as session:
            q = select(TaskORM).where(TaskORM.id == task_id)
            res = await session.execute(q)
            row = res.scalar_one_or_none()
            if row is None:
                raise TaskNotFoundError(task_id)
            return DomainTask(
                id=row.id,
                name=row.name,
                payload=row.payload,
                state=row.state,
                attempts=row.attempts,
                last_error=row.last_error,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )

    async def fetch_pending_outbox(self, limit: int = 50) -> List[EventOutboxORM]:
        """
        خواندن pending outbox با FOR UPDATE SKIP LOCKED برای جلوگیری از رقابت بین چند flusher
        """
        async with self._session_factory() as session:
            q = (
                select(EventOutboxORM)
                .where(EventOutboxORM.published == False)
                .order_by(EventOutboxORM.created_at)
                .limit(limit)
                .with_for_update(skip_locked=True)
            )
            res = await session.execute(q)
            rows = res.scalars().all()
            return rows

    async def mark_outbox_published(self, outbox_id: int, stream_id: str | None = None):
        async with self._session_factory() as session:
            async with session.begin():
                stmt = (
                    update(EventOutboxORM)
                    .where(EventOutboxORM.id == outbox_id)
                    .values(
                        published=True,
                        published_at=datetime.utcnow(),
                        stream_id=stream_id,
                    )
                )
                await session.execute(stmt)
