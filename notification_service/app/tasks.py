from celery import Celery
import os

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/1')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/2')

celery_app = Celery('notification_tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

@celery_app.task(bind=True)
def send_reminder(self, task_id: int, title: str):
    # здесь может быть интеграция с email/sms — сейчас просто логируем
    print(f"[Celery] Reminder for task {task_id}: {title}")
    return {'task_id': task_id, 'title': title}

@celery_app.task(bind=True)
def scheduled_check(self):
    # placeholder для периодических проверок (например, найти просроченные задачи)
    print('[Celery] Running scheduled check')
    return True
