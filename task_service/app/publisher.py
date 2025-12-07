import os
import json
import redis

REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')

def publish(channel: str, payload: dict):
    r = redis.from_url(REDIS_URL)
    r.publish(channel, json.dumps(payload))

