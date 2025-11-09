from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class TaskBase(BaseModel):
    user_id: str
    title: str
    category_id: Optional[int]
    description: Optional[str] = None
    expiration_date: Optional[datetime] = None
    is_completed: bool = False

class TaskCreate(TaskBase):
    pass

class TaskRead(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True