import threading
import json
import os
import redis
from .logger import log_event
from .tasks import send_reminder

REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
CHANNEL = 'tasks'

def consume():
    """Синхронный consumer для Redis pub/sub"""
    r = redis.from_url(REDIS_URL)
    pubsub = r.pubsub()
    pubsub.subscribe(CHANNEL)
    
    print('[Consumer] Subscribed to channel:', CHANNEL)
    
    for message in pubsub.listen():
        if message['type'] != 'message':
            continue
            
        try:
            data = json.loads(message['data'].decode('utf-8'))
        except Exception as e:
            print(f'Bad message: {e}')
            continue
        
        event = data.get('event')
        payload = data.get('task')
        
        # Логируем в БД
        log_event(event, payload)
        
        # Запускаем напоминание для новых задач
        if event == 'task_created':
            send_reminder.apply_async(
                args=(payload.get('id'), payload.get('title')),
                countdown=10
            )

def start_consumer_background():
    """Запускает consumer в фоновом потоке"""
    thread = threading.Thread(target=consume, daemon=True)
    thread.start()
    print('[Consumer] Started in background thread')