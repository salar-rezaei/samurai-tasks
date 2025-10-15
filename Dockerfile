
# Base image
FROM python:3.11-slim AS base


# System setup
WORKDIR /code
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1


# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev curl pkg-config \
    && rm -rf /var/lib/apt/lists/*


# Install Poetry
RUN pip install --no-cache-dir "poetry==1.8.3"


# Install dependencies
COPY pyproject.toml poetry.lock* /code/
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main

# Copy app source
COPY . /code/


# Default CMD (for API)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
