from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class NotificationIn(BaseModel):
    event: str
    task: dict

class NotificationOut(BaseModel):
    id: int
    event: str
    payload: dict
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
