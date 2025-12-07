from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from .database import Base

class NotificationLog(Base):
    __tablename__ = 'notification_logs'
    id = Column(Integer, primary_key=True, index=True)
    event = Column(String(100))
    payload = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
