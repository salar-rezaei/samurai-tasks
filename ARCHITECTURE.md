
---

## 🏯 `ARCHITECTURE.md`

```markdown
# 🏯 System Architecture – Samurai Tasks

---

## 🧩 Overview

Samurai Tasks is a **distributed, event-driven task orchestrator**.  
Its core philosophy: *every event deserves to be delivered once — and only once.*

The system ensures **data consistency** through the **Transactional Outbox pattern**,  
and enables scalable **asynchronous workers** powered by **Redis Streams**.

---

## 🏗️ Components

| Component | Role |
|------------|------|
| **FastAPI (app/api)** | Exposes HTTP endpoints for external clients |
| **PostgreSQL** | Stores persistent domain data & outbox events |
| **Redis Streams** | Message bus for inter-service communication |
| **Workers** | Consume events, execute side effects asynchronously |
| **Outbox** | Guarantees reliable delivery between DB and message bus |
| **Prometheus Client** | Exposes system metrics for observability |

---

## 🔁 Flow: Transactional Outbox Pattern

1. **Transaction Phase**  
   - When a domain action occurs (e.g., create task), a DB transaction is opened.  
   - The domain record and its corresponding **outbox event** are both persisted atomically.

2. **Dispatch Phase (Worker)**  
   - A background worker scans the outbox table.  
   - New events are published to **Redis Streams**.  
   - Once confirmed, the event is marked as “dispatched”.

3. **Consumption Phase (Consumers)**  
   - Worker services consume from Redis Streams in groups.  
   - Each consumer handles domain-specific logic (e.g., notifications, stats updates).

This ensures:
- **At-least-once** delivery
- **Eventual consistency**
- **Separation of concerns** between API and async workers

---

## 🧵 Concurrency Model

- **API**: ASGI-based, fully asynchronous (via Uvicorn + FastAPI)
- **Workers**: Event-loop consumers (Redis asyncio client)
- **DB Layer**: Async SQLAlchemy engine with connection pooling

---

## 🧰 Tech Stack

| Layer | Technology |
|--------|-------------|
| Framework | FastAPI |
| ORM | SQLAlchemy 2 (async) |
| Queue | Redis Streams |
| DB | PostgreSQL |
| Config | Pydantic Settings |
| Logging | structlog |
| Testing | pytest, testcontainers |
| Deployment | Docker + Compose |

---

## 🧠 Design Principles

- **DDD-inspired boundaries** (domain / infra / api)
- **Event-driven thinking**
- **Loose coupling**
- **Strong typing with Pydantic**
- **Observability-first** mindset

---

## ⚔️ Future Enhancements

- Tracing with OpenTelemetry  
- Dead-letter stream support  
- Horizontal scaling for workers  
- CLI for event replay & inspection

---

> *“A Samurai does not rush, yet he never hesitates.”*  
> — *Samurai Tasks Manifesto*
