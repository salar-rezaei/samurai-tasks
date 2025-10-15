# app/domain/models.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional
import uuid


@dataclass
class Task:
    """
    Domain entity
    """

    id: uuid.UUID
    name: str
    payload: Dict
    state: str = "pending"
    attempts: int = 0
    last_error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def new(cls, name: str, payload: Dict):
        return cls(id=uuid.uuid4(), name=name, payload=payload)
