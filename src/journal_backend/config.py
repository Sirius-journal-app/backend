"""Provide classes and functions for loading an application config."""
import logging
from dataclasses import dataclass

import toml

logger = logging.getLogger(__name__)

# You can replace this consts values with your own awesome ones :D
DEFAULT_APP_TITLE: str = "journal_backend"
DEFAULT_APP_DESCRIPTION: str = "Backend for the sirius-journal."
DEFAULT_APP_VERSION: str = "0.0.1"
DEFAULT_SERVER_HOST: str = "0.0.0.0"
DEFAULT_SERVER_PORT: int = 8000
DEFAULT_SERVER_LOG_LEVEL: str = "info"


@dataclass(kw_only=True)
class AppConfig:
    """Represent the application configuration.

    Attributes:
        title (str): The title of the application.
        description (str): The description of the application.
        jwt_secret (str): The JWT secret key for authentication.
    """

    title: str = DEFAULT_APP_TITLE
    description: str = DEFAULT_APP_DESCRIPTION
    version: str = DEFAULT_APP_VERSION
    jwt_secret: str
    jwt_lifetime_seconds: int = 60 * 60


@dataclass
class HttpServerConfig:
    """Represent the http server configuration.

    Attributes:
        host (str): The host of the server.
        port (int): The port of the server.
        log_level (str): The logging level of the server
    """

    host: str = DEFAULT_SERVER_HOST
    port: int = DEFAULT_SERVER_PORT
    log_level: str = DEFAULT_SERVER_LOG_LEVEL


@dataclass
class Database:
    """Represent the database configuration.

    Attributes:
        user (str): The username for the database connection.
        password (str): The password for the database connection.
        name (str): The name of the database.
        host (str): The host IP address for the database.
        port (int): The port number for the database.
    """

    user: str
    password: str
    name: str
    host: str
    port: int

    def __post_init__(self) -> None:
        """Initialise database URI."""
        self.uri = (
            f"postgresql+asyncpg://{self.user}:{self.password}@"  # noqa
            f"{self.host}:{self.port}/{self.name}"  # noqa
        )


@dataclass
class SMTPConfig:
    host: str
    email: str
    password: str
    port: int = 465

@dataclass
class RedisConfig:
    host: str = "localhost"
    port: int = 6379

    @property
    def uri(self) -> str:
        return f"redis://{self.host}:{self.port}/0"


@dataclass
class Config:
    """Represent the overall configuration of the project.

    Attributes:
        app (AppConfig): The application configuration.
        http_server (HttpServerConfig): The HTTP server configuration.
        db (Database): The database configuration.
        smtp (SMTPConfig): The SMTP server configuration.
    """

    app: AppConfig
    http_server: HttpServerConfig
    db: Database
    smtp: SMTPConfig
    redis: RedisConfig


def load_config(config_path: str) -> Config:
    """Load configuration from a TOML file.

    Returns:
        Config: An instance of the Config class containing the loaded configuration.
    """
    with open(config_path, "r") as config_file:
        data = toml.load(config_file)
    return Config(
        app=AppConfig(**data["app"]),
        http_server=HttpServerConfig(**data["http_server"]),
        db=Database(**data["db"]),
        smtp=SMTPConfig(**data["smtp"]),
        redis=RedisConfig(**data["redis"]),
    )
