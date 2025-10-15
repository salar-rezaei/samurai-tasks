# app/infra/db/sqlalchemy_models.py
from sqlalchemy import Column, String, Integer, DateTime, JSON, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()


class TaskORM(Base):
    __tablename__ = "tasks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    payload = Column(JSON, nullable=False, default={})
    state = Column(String, default="pending", nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    last_error = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class EventOutboxORM(Base):
    __tablename__ = "outbox_events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    stream = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    published = Column(Boolean, nullable=False, default=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    stream_id = Column(String, nullable=True)
