import json
from .database import SessionLocal
from . import models

def log_event(event: str, payload: dict):
    db = SessionLocal()
    try:
        log = models.NotificationLog(event=event, payload=json.dumps(payload))
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    finally:
        db.close()
