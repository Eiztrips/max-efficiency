from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import Optional

# --------------- REQUEST -------------------

class TagCreate(BaseModel):
    category_id: int
    name: str
    color: Optional[str] = "#FFFFFF"

class TagUpdate(BaseModel):
    id: int
    category_id: Optional[int] = None
    name: Optional[str] = None
    color: Optional[str] = None

# --------------- RESPONSE -------------------

class TagRead(BaseModel):
    id: int
    name: str
    color: str = "#FFFFFF"
    category_id: int

    tasks: Optional[list[int]] = []

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_validator('tasks', mode='before')
    @classmethod
    def extract_ids(cls, value):
        if value is None:
            return []
        if isinstance(value, list):
            return [item.id if hasattr(item, 'id') else item for item in value]
        return value