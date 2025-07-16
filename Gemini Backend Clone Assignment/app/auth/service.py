import random
import string
import time
import jwt
from app.core.config import settings

OTP_TTL = 300  # 5 minutes

# Placeholder Redis client
class RedisClient:
    _store = {}
    def set(self, key, value, ex=None):
        self._store[key] = (value, time.time() + (ex or OTP_TTL))
    def get(self, key):
        val = self._store.get(key)
        if not val:
            return None
        value, expires = val
        if time.time() > expires:
            del self._store[key]
            return None
        return value
    def delete(self, key):
        if key in self._store:
            del self._store[key]

redis_client = RedisClient()

def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

def store_otp(mobile, otp):
    redis_client.set(f"otp:{mobile}", otp, ex=OTP_TTL)

def verify_otp(mobile, otp):
    stored = redis_client.get(f"otp:{mobile}")
    if stored and stored == otp:
        redis_client.delete(f"otp:{mobile}")
        return True
    return False

def create_jwt_token(user_id):
    payload = {"user_id": user_id}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

def decode_jwt_token(token):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return payload
    except Exception:
        return None 