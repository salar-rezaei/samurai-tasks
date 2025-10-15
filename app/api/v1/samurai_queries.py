# app/api/v1/queries.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel
from app.domain.services_async import TaskServiceAsync
from app.infra.db.repo_async import AsyncTaskRepository

router = APIRouter(prefix="/v1/tasks", tags=["tasks"])


class TaskRead(BaseModel):
    id: str
    name: str
    payload: dict
    state: str
    attempts: int
    last_error: Optional[str] = None


def get_task_service() -> TaskServiceAsync:
    repo = AsyncTaskRepository()
    return TaskServiceAsync(repo)


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(task_id: str, svc: TaskServiceAsync = Depends(get_task_service)):
    try:
        t = await svc.get_task(task_id)
        return TaskRead(
            id=str(t.id),
            name=t.name,
            payload=t.payload,
            state=t.state,
            attempts=t.attempts,
            last_error=t.last_error,
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail="task not found")
