import asyncio
import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from sqlalchemy.schema import CreateSchema

from api.dependencies import uow_dependency
from db.db import Base
from main import app
from utils.unitofwork import UnitOfWork

# 1. Настройки подключения
TEST_DB_HOST = os.environ.get("TEST_DB_HOST", "localhost")
TEST_DB_PORT = os.environ.get("TEST_DB_PORT", "5433")
TEST_DB_NAME = os.environ.get("TEST_DB_NAME", "test_db")
TEST_DB_USER = os.environ.get("TEST_DB_USER", "test_user")
TEST_DB_PASS = os.environ.get("TEST_DB_PASS", "test_password")

TEST_DATABASE_URL = (
    f"postgresql+asyncpg://{TEST_DB_USER}:{TEST_DB_PASS}@"
    f"{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"
)
test_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
TestSessionMaker = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


# 2. Переопределение зависимости UoW
@pytest_asyncio.fixture(scope="function")
async def get_test_uow(db_session: AsyncSession) -> AsyncGenerator:
    # Создаем временную Unit of Work специально для этого теста
    class TestUnitOfWork(UnitOfWork):
        def __init__(self):
            # Она будет использовать ТУ ЖЕ сессию, что и сам тест
            self._session = db_session

        async def __aexit__(self, *args):
            pass

        async def __aenter__(self):
            await super().__aenter__()
            return self

    test_uow = TestUnitOfWork()

    def _override_get_uow():
        return test_uow

    app.dependency_overrides[uow_dependency] = _override_get_uow
    yield test_uow
    app.dependency_overrides.clear()


# 3. Фикстура для event loop
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# 4. Фикстура для подготовки БД, которая СОЗДАЕТ СХЕМЫ
@pytest_asyncio.fixture(scope="session")
async def setup_database(event_loop):
    schemas_to_create = set(
        table.schema for table in Base.metadata.tables.values() if table.schema
    )
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        for schema in schemas_to_create:
            await conn.execute(CreateSchema(schema, if_not_exists=True))

        await conn.run_sync(Base.metadata.create_all)

    yield

    await test_engine.dispose()


# 5. Фикстура для транзакционной сессии
@pytest_asyncio.fixture(scope="function")
async def db_session(setup_database) -> AsyncGenerator[AsyncSession, None]:
    async with test_engine.connect() as connection:
        async with connection.begin() as transaction:
            async with TestSessionMaker(bind=connection) as session:
                yield session
                await transaction.rollback()


# 6. Фикстура для клиента
@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
