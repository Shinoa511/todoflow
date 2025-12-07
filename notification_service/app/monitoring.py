from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from .database import SessionLocal
from . import models
import redis
import json
import os

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

# Зависимость для БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Общая статистика"""
    total_events = db.query(func.count(models.NotificationLog.id)).scalar() or 0
    
    # Статистика по типам событий
    event_stats = db.query(
        models.NotificationLog.event,
        func.count(models.NotificationLog.id).label('count')
    ).group_by(models.NotificationLog.event).all()
    
    # Последние события
    recent_events = db.query(models.NotificationLog).order_by(
        models.NotificationLog.created_at.desc()
    ).limit(10).all()
    
    # Redis статус
    redis_status = "unknown"
    try:
        r = redis.from_url(os.getenv('REDIS_URL', 'redis://redis:6379/0'))
        redis_status = "connected" if r.ping() else "disconnected"
    except:
        redis_status = "error"
    
    return {
        "total_events": total_events,
        "events_by_type": {event: count for event, count in event_stats},
        "redis_status": redis_status,
        "recent_events": [
            {
                "id": e.id,
                "event": e.event,
                "created_at": e.created_at.isoformat() if e.created_at else None,
                "payload": json.loads(e.payload) if e.payload else {}
            } for e in recent_events
        ]
    }

@router.get("/events")
def get_events(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Список всех событий с пагинацией"""
    events = db.query(models.NotificationLog).order_by(
        models.NotificationLog.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    total = db.query(func.count(models.NotificationLog.id)).scalar()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "events": [
            {
                "id": e.id,
                "event": e.event,
                "payload": json.loads(e.payload) if e.payload else {},
                "created_at": e.created_at.isoformat() if e.created_at else None
            } for e in events
        ]
    }

@router.get("/celery-tasks")
def get_celery_tasks():
    """Статус Celery задач (заглушка, можно расширить)"""
    return {
        "tasks_registered": ["send_reminder", "scheduled_check"],
        "note": "Для детальной статистики используйте Flower: http://localhost:5555"
    }

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Проверка здоровья сервиса"""
    # Проверка БД
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except:
        db_status = "error"
    
    # Проверка Redis
    redis_status = "ok"
    try:
        r = redis.from_url(os.getenv('REDIS_URL', 'redis://redis:6379/0'))
        redis_status = "connected" if r.ping() else "disconnected"
    except:
        redis_status = "error"
    
    return {
        "status": "healthy" if db_status == "ok" and redis_status == "connected" else "degraded",
        "database": db_status,
        "redis": redis_status,
        "service": "notification"
    }