import asyncio
import subprocess
import time
from asyncio import AbstractEventLoop
from typing import AsyncGenerator, Generator, TypeAlias

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from redis.asyncio import ConnectionPool, Connection, Redis
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

from journal_backend.app_setup import (
    create_app,
    initialise_dependencies,
    initialise_routers,
)
from journal_backend.config import Config, load_config
from journal_backend.database.base import Base
from journal_backend.database.dependencies import create_session
from journal_backend.database.sa_utils import create_session_maker
from journal_backend.entity.models import *  # noqa

from journal_backend.entity.users.models import UserIdentity
from journal_backend.entity.users.repository import UserRepository
from journal_backend.entity.users.service import UserService

BASE_URL = "http://test"
TEST_CONFIG_PATH = ".configs/test.toml"

SessionMaker: TypeAlias = sessionmaker[AsyncSession]


@pytest.fixture(scope="session")
def event_loop() -> Generator[AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def config() -> Config:
    return load_config(TEST_CONFIG_PATH)


@pytest_asyncio.fixture(scope="session")
async def redis_pool(config: Config):
    redis_pool: ConnectionPool[Connection] = ConnectionPool.from_url(config.redis.uri)
    yield redis_pool
    await redis_pool.aclose()


@pytest_asyncio.fixture(scope="session")
async def redis_conn(redis_pool):
    conn = Redis.from_pool(redis_pool)  # type:ignore
    yield conn


@pytest.fixture(scope="session")
def app(config: Config, redis_pool) -> FastAPI:
    app = create_app(config.app)
    initialise_routers(app)
    initialise_dependencies(app, config, redis_pool)
    return app


@pytest_asyncio.fixture(scope="session")
async def client(app: FastAPI, config: Config) -> AsyncClient:
    async with AsyncClient(
            app=app,
            base_url=config.http_server.host,
            headers={"Accept": "application/json"},
    ) as ac:
        yield ac


@pytest.fixture(scope="session")
def initialise_test_db(config: Config) -> None:
    subprocess.run(
        "docker run "
        "--name journal-backend-pgsql-test "
        f"-e POSTGRES_USER={config.db.user} "
        f"-e POSTGRES_PASSWORD={config.db.password} "
        f"-e POSTGRES_DB={config.db.name} "
        f"-p {config.db.port}:5432 "
        "-d postgres"
    )
    time.sleep(2)  # waiting until the database is ready to accept connections
    yield
    subprocess.run("docker stop journal-backend-pgsql-test")
    subprocess.run("docker rm journal-backend-pgsql-test")


@pytest.fixture(scope="session")
def initialise_test_redis(config: Config) -> None:
    subprocess.run(
        "docker run "
        "--name journal-backend-redis-test "
        f"-p {config.redis.port}:6379 "
        "-d postgres"
    )
    time.sleep(2)  # waiting until the database is ready to accept connections
    yield
    subprocess.run("docker stop journal-backend-test")
    subprocess.run("docker rm journal-backend-test")


@pytest.fixture(scope="session")
def engine(config: Config, initialise_test_db: ...) -> AsyncEngine:
    return create_async_engine(config.db.uri, echo=True)


@pytest_asyncio.fixture(scope="session")
async def initialise_migrations(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
def session_factory(engine: AsyncEngine) -> SessionMaker:
    session_maker = create_session_maker(engine)
    return session_maker


@pytest_asyncio.fixture(scope="session")
async def session(
        session_factory: SessionMaker,
) -> AsyncGenerator[AsyncSession, None]:
    async with create_session(session_factory) as async_session:
        yield async_session


@pytest.fixture(scope="session")
def user_service(session: AsyncSession, config: Config, redis_conn) -> UserService:
    return UserService(UserRepository(session, UserIdentity), config.app.jwt_secret, redis_conn)
