from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

NOTIF_DB_USER = os.getenv('NOTIF_DB_USER', 'notif_user')
NOTIF_DB_PASSWORD = os.getenv('NOTIF_DB_PASSWORD', 'notif_pass')
NOTIF_DB_HOST = os.getenv('NOTIF_DB_HOST', 'notification_db')
NOTIF_DB_PORT = os.getenv('NOTIF_DB_PORT', '5432')
NOTIF_DB_NAME = os.getenv('NOTIF_DB_NAME', 'notification_db')

DATABASE_URL = f'postgresql+psycopg2://{NOTIF_DB_USER}:{NOTIF_DB_PASSWORD}@{NOTIF_DB_HOST}:{NOTIF_DB_PORT}/{NOTIF_DB_NAME}'

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    from .models import NotificationLog
    Base.metadata.create_all(bind=engine)
