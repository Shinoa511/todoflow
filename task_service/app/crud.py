from sqlalchemy.orm import Session
from . import models, schemas

def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Task).offset(skip).limit(limit).all()

def create_task(db: Session, task: schemas.TaskCreate):
    db_task = models.Task(title=task.title, description=task.description, due_date=task.due_date)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, db_task, updates: schemas.TaskUpdate):
    for k, v in updates.dict(exclude_unset=True).items():
        setattr(db_task, k, v)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, db_task):
    db.delete(db_task)
    db.commit()
    return True
