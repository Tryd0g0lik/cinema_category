"""
wink/redis_utils.py
"""

from django.conf import settings

try:
    import redis
except ImportError:
    redis = None


def get_redis_client():
    if redis is None:
        raise RuntimeError("Please install redis-py (pip install redis)")
    url = getattr(settings, "REDIS_URL", None)
    if not url:
        raise RuntimeError("Please install redis-py (pip install redis)")
    return redis.from_url(url, decode_responses=True)
