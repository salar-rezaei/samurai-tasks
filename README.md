# 🥷 Samurai Tasks

Event-driven task orchestration system built with **FastAPI**, **Redis Streams**, and **PostgreSQL**, following a **Transactional Outbox** pattern for reliable event delivery.

---

## 🚀 Features

- **Event-driven architecture** using Redis Streams as message bus  
- **Transactional outbox** for guaranteed delivery of domain events  
- **Asynchronous workers** for background task processing  
- **FastAPI** for HTTP APIs  
- **PostgreSQL** as the main persistence layer  
- **Structured logging** with `structlog`  
- **Prometheus metrics** ready for observability  

---


## ⚙️ Setup

### 1️⃣ Prerequisites
- Docker & Docker Compose
- Python 3.11 (if running locally)
- Poetry (`pip install poetry`)

---

### 2️⃣ Run with Docker (recommended)

```bash
docker compose up --build
```
This will start:

- samurai_api → FastAPI service on http://localhost:8000

- go to http://localhost:8000/docs to see api's

- samurai_worker_1, samurai_worker_2 → background event consumers

- Postgres → localhost:5432

- Redis → localhost:6379

### 3️⃣ Run locally (optional)

```bash
poetry install
cp .env.example .env
```
- Set POSTGRES_HOST and REDIS_HOST to "localhost" in .env file (for run locally)
```
poetry run uvicorn app.main:app --reload
```
- Then open terminal and run worker with this command:
```
python -m app.workers.consumer_entrypoint
```

### 🧠 Environment Variables

| Variable               | Description                       | Example                                                        |
| ---------------------- | --------------------------------- | -------------------------------------------------------------- |
| `APP_ENV`              | Application environment           | `"dev"`                                                        |
| `APP_NAME`             | Application name                  | `"SamuraiTasks"`                                               |
| `APP_DEBUG`            | Enables debug mode                | `True`                                                         |
| `APP_HOST`             | Host address for FastAPI server   | `"0.0.0.0"`                                                    |
| `APP_PORT`             | Port number for API service       | `8000`                                                         |
| `POSTGRES_DB`          | PostgreSQL database name          | `"samurai"`                                                    |
| `POSTGRES_USER`        | PostgreSQL username               | `"postgres"`                                                   |
| `POSTGRES_PASSWORD`    | PostgreSQL password               | `"postgres"`                                                   |
| `POSTGRES_HOST`        | Hostname of PostgreSQL service    | `"postgres"`                                                   |
| `POSTGRES_PORT`        | Port for PostgreSQL               | `5432`                                                         |
| `DATABASE_URL`         | Full async connection URL         | `postgresql+asyncpg://postgres:postgres@postgres:5432/samurai` |
| `REDIS_HOST`           | Redis hostname                    | `"redis"`                                                      |
| `REDIS_PORT`           | Redis port                        | `6379`                                                         |
| `REDIS_DB`             | Redis database index              | `0`                                                            |
| `REDIS_URL`            | Full Redis connection URL         | `redis://redis:6379/0`                                         |
| `STREAM_NAME`          | Redis stream name used for events | `"tasks:events"`                                               |
| `CONSUMER_GROUP`       | Redis consumer group name         | `"samurai_group"`                                              |
| `CONSUMER_NAME`        | Redis consumer name               | `"samurai_worker"`                                             |
| `CONSUMER_PORT`        | Port for worker service           | `8001`                                                         |
| `LOCK_TTL`             | Lock time-to-live (milliseconds)  | `5000`                                                         |
| `OUTBOX_POLL_INTERVAL` | Outbox polling interval (seconds) | `0.5`                                                          |
| `LOG_LEVEL`            | Application log level             | `INFO`                                                         |



___
___

## 👤 Author
Salar Rezaei >
Software engineer | Python, Django, FastAPI | 武士道

- 💼 LinkedIn: [salar-rezaei](https://www.linkedin.com/in/salar-rezaei/)
- 📧 Email: salarrezaei26@gmail.com
