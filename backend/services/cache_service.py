import os, hashlib
import redis.asyncio as aioredis
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

REDIS_URL   = os.getenv("REDIS_URL", "redis://localhost:6379")
CACHE_TTL   = 3600
RATE_WINDOW = 60
RATE_LIMIT  = 30

_redis = None

async def get_redis():
    global _redis
    if _redis is None:
        _redis = await aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis

def _cache_key(file_id: str, question: str) -> str:
    h = hashlib.md5(f"{file_id}:{question}".encode()).hexdigest()
    return f"qa:{h}"

async def get_cached_answer(file_id: str, question: str) -> Optional[str]:
    try:
        r = await get_redis()
        return await r.get(_cache_key(file_id, question))
    except Exception:
        return None

async def set_cached_answer(file_id: str, question: str, answer: str) -> None:
    try:
        r = await get_redis()
        await r.setex(_cache_key(file_id, question), CACHE_TTL, answer)
    except Exception:
        pass

async def check_rate_limit(user_id: str) -> bool:
    try:
        r   = await get_redis()
        key = f"rate:{user_id}"
        cnt = await r.incr(key)
        if cnt == 1:
            await r.expire(key, RATE_WINDOW)
        return cnt <= RATE_LIMIT
    except Exception:
        return True
