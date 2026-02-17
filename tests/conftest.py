import pytest
from typing import AsyncGenerator
from httpx import ASGITransport, AsyncClient
import asyncio
import time

from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    AsyncEngine,
    async_sessionmaker
)

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Создаёт event loop для всей сессии."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    time.sleep(0.1)
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()
    asyncio.set_event_loop(None)


@pytest.fixture(scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Движок для тестовой базы данных."""
    test_db_url = settings.DATABASE_URL.replace("todo_db", "todo_test_db")
    engine = create_async_engine(
        url=test_db_url,
        echo=True,
        poolclass=NullPool,
    )
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture(scope="session")
async def create_tables(test_engine: AsyncEngine):
    """Создаёт таблицы один раз за сессию."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Не удаляем таблицы после сессии,
    # чтобы они были доступны для всех тестов


@pytest.fixture(autouse=True)
async def clean_tables(test_engine: AsyncEngine):
    """Очищает все таблицы перед каждым тестом."""
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest.fixture
async def session(
    test_engine: AsyncEngine,
    create_tables,  # гарантируем, что таблицы созданы
    clean_tables    # гарантируем, что таблицы чистые
) -> AsyncGenerator[AsyncSession, None]:
    """Сессия для каждого теста с чистой базой данных."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest.fixture
async def client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Клиент для тестирования эндпоинтов с подменённой зависимостью БД."""

    async def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
