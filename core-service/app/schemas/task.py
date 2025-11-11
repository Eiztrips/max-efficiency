from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import Optional

# --------------- REQUEST -------------------

class TaskCreate(BaseModel):
    user_id: int
    title: str
    description: Optional[str] = None
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
    user_id: int
    title: str
    description: Optional[str]
    expiration_date: Optional[datetime] = None
    is_completed: bool

    created_at: datetime
    updated_at: datetime

    category_id: int
    tags: Optional[list[int]] = []

    model_config = {"from_attributes": True}

    @field_validator('tags', mode='before')
    @classmethod
    def extract_ids(cls, value):
        if value is None:
            return []
        if isinstance(value, list):
            return [item.id if hasattr(item, 'id') else item for item in value]
        return value