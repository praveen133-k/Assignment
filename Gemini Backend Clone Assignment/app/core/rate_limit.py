import redis
from app.core.config import settings
from datetime import datetime, timedelta

if not settings.REDIS_URL:
    raise ValueError("REDIS_URL is not set in environment variables.")

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

BASIC_DAILY_LIMIT = 5

# Key: rate:user:{user_id}:{date}
def get_rate_limit_key(user_id):
    today = datetime.utcnow().strftime('%Y-%m-%d')
    return f"rate:user:{user_id}:{today}"

def check_rate_limit(user_id):
    key = get_rate_limit_key(user_id)
    count = redis_client.get(key)
    if count is None or not isinstance(count, str):
        return 0
    return int(count)

def increment_rate_limit(user_id):
    key = get_rate_limit_key(user_id)
    ttl = 86400  # 1 day
    pipe = redis_client.pipeline()
    pipe.incr(key, 1)
    pipe.expire(key, ttl)
    pipe.execute() 