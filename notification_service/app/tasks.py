# notification_service/app/tasks.py
from celery import Celery
import os
import requests
from datetime import datetime, timezone
from dateutil import parser as date_parser
from . import publisher
from .logger import log_event
from .database import SessionLocal
from . import models

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/1')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/2')

celery_app = Celery('notification_tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

# Beat schedule: периодический вызов scheduled_check каждые 30 секунд (демонстрационный режим)
celery_app.conf.beat_schedule = {
    'scheduled-check-every-30s': {
        'task': 'app.tasks.scheduled_check',
        'schedule': 30.0,
    }
}
celery_app.conf.timezone = 'UTC'


@celery_app.task(bind=True)
def send_reminder(self, task_id: int, title: str):
    # здесь может быть интеграция с email/sms — сейчас просто логируем
    print(f"[Celery] Reminder for task {task_id}: {title}")
    return {'task_id': task_id, 'title': title}


@celery_app.task(bind=True, name='app.tasks.scheduled_check')
def scheduled_check(self):
    """
    Проверка каждые 30 секунд через Celery Beat:
    1. Находит просроченные задачи → создает task_due событие
    2. Находит задачи с наступившим due_date → отправляет reminder
    3. Все напоминания отправляются НЕМЕДЛЕННО (countdown=0)
    """
    TASK_SERVICE_URL = os.getenv('TASK_SERVICE_URL', 'http://task_service:8000')
    try:
        resp = requests.get(f"{TASK_SERVICE_URL}/tasks?limit=1000", timeout=10)
        resp.raise_for_status()
        tasks = resp.json()
    except Exception as e:
        print(f"[scheduled_check] Error fetching tasks: {e}")
        return {'ok': False, 'error': str(e)}

    now = datetime.now(timezone.utc)
    db = SessionLocal()
    
    try:
        task_due_processed = 0
        reminders_sent = 0
        
        for t in tasks:
            task_id = t.get('id')
            due_str = t.get('due_date')
            title = t.get('title') or ''
            
            if not due_str:
                continue
                
            try:
                due_dt = date_parser.isoparse(due_str)
            except Exception as e:
                print(f"[scheduled_check] Can't parse due_date for task {task_id}: {due_str}")
                continue

            # Приводим дату к UTC
            if due_dt.tzinfo is None:
                due_dt = due_dt.replace(tzinfo=timezone.utc)
            
            # 1. ПРОВЕРКА ПРОСРОЧЕННЫХ ЗАДАЧ (task_due)
            if due_dt <= now:
                # Проверяем, есть ли уже лог task_due
                task_due_exists = db.query(models.NotificationLog).filter(
                    models.NotificationLog.event == 'task_due',
                    models.NotificationLog.payload.ilike(f'%"id": {task_id}%')
                ).first()

                if not task_due_exists:
                    # Создаем событие task_due
                    payload = {
                        'event': 'task_due',
                        'task': {'id': task_id, 'title': title, 'due_date': due_str}
                    }
                    
                    try:
                        publisher.publish('tasks', payload)
                        log_event('task_due', payload['task'])
                        print(f"[scheduled_check] Published task_due for task {task_id}")
                    except Exception as e:
                        print(f"[scheduled_check] Error logging task_due: {e}")
                    
                    task_due_processed += 1
            
            # 2. ПРОВЕРКА ДЛЯ НАПОМИНАНИЙ
            # Отправляем напоминание, если due_date уже наступил
            if due_dt <= now:
                # Проверяем, не отправляли ли уже напоминание
                reminder_sent = db.query(models.NotificationLog).filter(
                    models.NotificationLog.event == 'reminder_sent',
                    models.NotificationLog.payload.ilike(f'%"task_id": {task_id}%')
                ).first()
                
                if not reminder_sent:
                    # Отправляем напоминание НЕМЕДЛЕННО
                    try:
                        send_reminder.apply_async(args=(task_id, title), countdown=0)
                        
                        # Записать что напоминание отправлено
                        log_event('reminder_sent', {
                            'task_id': task_id,
                            'title': title,
                            'due_date': due_str,
                            'sent_at': now.isoformat(),
                            'was_overdue': due_dt < now
                        })
                        
                        reminders_sent += 1
                        print(f"[scheduled_check] Sent reminder for task {task_id}")
                            
                    except Exception as e:
                        print(f"[scheduled_check] Failed to send reminder for {task_id}: {e}")
        
        return {
            'ok': True, 
            'task_due_processed': task_due_processed,
            'reminders_sent': reminders_sent,
            'checked_at': now.isoformat()
        }
        
    finally:
        db.close()