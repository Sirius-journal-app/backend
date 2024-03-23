import asyncio

from journal_backend.app_setup import (
    create_app,
    initialise_dependencies,
    initialise_routers,
)
from journal_backend.config import load_config
from journal_backend.consts import CONFIG_PATH
from journal_backend.app_setup import create_http_server


async def main() -> None:
    config = load_config(CONFIG_PATH)
    app = create_app(config.app)

    initialise_routers(app)
    initialise_dependencies(app, config)

    server = create_http_server(app, config.http_server)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())