"""Application entry point."""

import asyncio
import sys

from redis.asyncio import ConnectionPool
from redis.asyncio.connection import Connection

from journal_backend.app_setup import (
    create_app,
    create_http_server,
    initialise_dependencies,
    initialise_routers,
)
from journal_backend.config import load_config
from journal_backend.consts import CONFIG_PATH


async def main() -> None:
    """Set up application and start http server."""
    config = load_config(CONFIG_PATH)
    app = create_app(config.app)

    initialise_routers(app)

    redis_pool: ConnectionPool[Connection] = ConnectionPool.from_url(config.redis.uri)
    initialise_dependencies(app, config, redis_pool)

    server = create_http_server(app, config.http_server)
    try:
        await server.serve()
    finally:
        await redis_pool.aclose()  # type:ignore[attr-defined]


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())

