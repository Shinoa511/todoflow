from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
import os

TASK_DB_USER = os.getenv('TASK_DB_USER', 'task_user')
TASK_DB_PASSWORD = os.getenv('TASK_DB_PASSWORD', 'task_pass')
TASK_DB_HOST = os.getenv('TASK_DB_HOST', 'task_db')
TASK_DB_PORT = os.getenv('TASK_DB_PORT', '5432')
TASK_DB_NAME = os.getenv('TASK_DB_NAME', 'task_db')

DATABASE_URL = f'postgresql+psycopg2://{TASK_DB_USER}:{TASK_DB_PASSWORD}@{TASK_DB_HOST}:{TASK_DB_PORT}/{TASK_DB_NAME}'

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# helper
def init_db():
    from .models import Task
    Base.metadata.create_all(bind=engine)
