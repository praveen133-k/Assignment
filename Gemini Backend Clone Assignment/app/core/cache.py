import redis
import json
from app.core.config import settings

if not settings.REDIS_URL:
    raise ValueError("REDIS_URL is not set in environment variables.")

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

CHATROOM_CACHE_TTL = 600  # 10 minutes

def cache_chatrooms(user_id, chatrooms):
    key = f"chatrooms:{user_id}"
    redis_client.setex(key, CHATROOM_CACHE_TTL, json.dumps(chatrooms))

def get_cached_chatrooms(user_id):
    key = f"chatrooms:{user_id}"
    data = redis_client.get(key)
    if data and isinstance(data, str):
        return json.loads(data)
    return None

def invalidate_chatroom_cache(user_id):
    key = f"chatrooms:{user_id}"
    redis_client.delete(key) 