"""Database connection setup (PostgreSQL + PostGIS via asyncpg/SQLAlchemy).

TODO(PROPWASH): Implement migrations in db/migrations/ using Alembic.
This module establishes the async engine and session factory.
Set DATABASE_URL env var: postgresql+asyncpg://user:pass@host/propwash
"""

from __future__ import annotations

import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+asyncpg://propwash:propwash@localhost/propwash"
)

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
