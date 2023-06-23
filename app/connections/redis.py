import redis
from redis import asyncio as aioredis

from app.settings import settings

redis_client_async = None
redis_client = None


def get_redis_client_async():
    global redis_client_async

    if redis_client_async is None:
        redis_client_async = aioredis.from_url(settings.REDIS.url)
    return redis_client_async


def get_redis_client():
    global redis_client

    if redis_client is None:
        redis_client = redis.from_url(settings.REDIS.url)
    return redis_client
