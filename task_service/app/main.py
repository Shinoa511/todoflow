from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import database, models, crud, schemas, publisher
import os

app = FastAPI(title="Task Service")

# create DB at startup
@app.on_event('startup')
def startup():
    database.init_db()

# dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post('/tasks', response_model=schemas.TaskOut)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    db_task = crud.create_task(db, task)
    # publish event
    payload = {
        'event': 'task_created',
        'task': {
            'id': db_task.id,
            'title': db_task.title,
            'due_date': db_task.due_date.isoformat() if db_task.due_date else None
        }
    }
    publisher.publish('tasks', payload)
    return db_task

@app.get('/tasks', response_model=list[schemas.TaskOut])
def list_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_tasks(db, skip=skip, limit=limit)

@app.get('/tasks/{task_id}', response_model=schemas.TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    db_task = crud.get_task(db, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail='Task not found')
    return db_task

@app.put('/tasks/{task_id}', response_model=schemas.TaskOut)
def update_task(task_id: int, updates: schemas.TaskUpdate, db: Session = Depends(get_db)):
    db_task = crud.get_task(db, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail='Task not found')
    db_task = crud.update_task(db, db_task, updates)
    payload = {'event': 'task_updated', 'task': {'id': db_task.id, 'title': db_task.title}}
    publisher.publish('tasks', payload)
    return db_task

@app.delete('/tasks/{task_id}')
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = crud.get_task(db, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail='Task not found')
    crud.delete_task(db, db_task)
    payload = {'event': 'task_deleted', 'task': {'id': task_id}}
    publisher.publish('tasks', payload)
    return {'ok': True}
