import redis.asyncio as redis
from app.config import REDIS_HOST, REDIS_PORT

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=int(REDIS_PORT),
    decode_responses=True,
)


async def get_redis():
    return redis_client