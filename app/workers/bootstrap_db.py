# app/workers/bootstrap_db.py
import asyncio
import logging
from app.infra.db.repo_async import create_tables

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bootstrap")


async def main():
    logger.info("Starting database bootstrap...")
    await create_tables()
    logger.info("Database tables created successfully!")


if __name__ == "__main__":
    asyncio.run(main())
