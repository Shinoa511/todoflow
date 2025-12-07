# notification_service/app/publisher.py
import os
import json
import redis

REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')

def publish(channel: str, payload: dict):
    """Publish JSON payload to Redis channel."""
    r = redis.from_url(REDIS_URL)
    r.publish(channel, json.dumps(payload))
