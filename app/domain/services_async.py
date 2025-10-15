# app/domain/services_async.py

from app.domain.models import Task as DomainTask
from app.infra.db.repo_async import AsyncTaskRepository
import uuid


class TaskServiceAsync:
    """
    سرویس بیزینسی async — وابسته به رابط repository async
    """

    def __init__(self, repo: AsyncTaskRepository):
        self.repo = repo

    async def create_task(self, name: str, payload: dict) -> DomainTask:
        task = DomainTask(id=uuid.uuid4(), name=name, payload=payload)
        outbox_event = {
            "stream": "tasks:events",
            "event_type": "task.created",
            "payload": {"name": name, "payload": payload},
        }
        await self.repo.add_task_with_outbox(task, outbox_event)
        return task

    async def get_task(self, task_id):
        return await self.repo.get_task(task_id)
