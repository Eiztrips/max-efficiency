from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

# --------------- REQUEST -------------------

class TaskCreate(BaseModel):
    user_id: int
    title: str
    description: Optional[str]
    expiration_date: Optional[datetime] = None
    is_completed: bool = False
    category_id: Optional[int]

class TaskUpdate(BaseModel):
    id: int
    title: Optional[str] = None
    description: Optional[str] = None
    expiration_date: Optional[datetime] = None
    is_completed: Optional[bool] = None
    category_id: Optional[int] = None

class TaskQuery(BaseModel):
    user_id: int
    category_id: Optional[int] = None
    tag_id: Optional[int] = None
    status: Optional[str] = None
    is_completed: Optional[bool] = None
    from_date: Optional[str] = None
    to_date: Optional[str] = None
    search: Optional[str] = None

# --------------- RESPONSE -------------------

class TaskRead(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

