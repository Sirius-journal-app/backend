from redis.asyncio import ConnectionPool, Redis

from journal_backend.entity.common.email_sender import EmailSender


def get_email_sender():
    yield EmailSender()


async def get_redis_conn(pool: ConnectionPool):
    conn = Redis.from_pool(pool)
    yield conn
