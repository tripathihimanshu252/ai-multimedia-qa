import os

# Redis is optional - gracefully disabled if not available
try:
    import redis
    _REDIS_URL = os.getenv("REDIS_URL", "")
    if _REDIS_URL:
        _client = redis.from_url(_REDIS_URL, decode_responses=True, socket_connect_timeout=2)
        _client.ping()
        REDIS_AVAILABLE = True
        print("✅ Redis connected")
    else:
        raise ValueError("No REDIS_URL set")
except Exception as e:
    REDIS_AVAILABLE = False
    _client = None
    print(f"⚠️ Redis not available: {e} - caching disabled")

def get_cached_answer(key: str):
    if not REDIS_AVAILABLE:
        return None
    try:
        return _client.get(key)
    except Exception:
        return None

def set_cached_answer(key: str, value: str, ttl: int = 3600):
    if not REDIS_AVAILABLE:
        return
    try:
        _client.setex(key, ttl, value)
    except Exception:
        pass

def check_rate_limit(user_id: str, limit: int = 20) -> bool:
    if not REDIS_AVAILABLE:
        return True  # allow all requests when Redis is down
    try:
        key = f"rate:{user_id}"
        count = _client.incr(key)
        if count == 1:
            _client.expire(key, 60)
        return count <= limit
    except Exception:
        return True
