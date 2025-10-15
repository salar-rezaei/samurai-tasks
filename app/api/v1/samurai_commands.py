# app/api/v1/commands.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict
from app.domain.services_async import TaskServiceAsync
from app.infra.db.repo_async import AsyncTaskRepository

router = APIRouter(prefix="/v1/tasks", tags=["tasks"])


class CreateTaskRequest(BaseModel):
    name: str
    payload: Dict = {}


# dependency factory
def get_task_service() -> TaskServiceAsync:
    repo = AsyncTaskRepository()
    return TaskServiceAsync(repo)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_task(
    req: CreateTaskRequest, svc: TaskServiceAsync = Depends(get_task_service)
):
    try:
        task = await svc.create_task(req.name, req.payload)
        return {"id": str(task.id), "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
