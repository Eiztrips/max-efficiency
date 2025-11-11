from datetime import datetime
from pydantic import BaseModel
from typing import Optional

# --------------- REQUEST -------------------

class CategoryCreate(BaseModel):
    user_id: int
    name: str
    description: Optional[str] = None

# --------------- RESPONSE -------------------

class CategoryRead(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class CategoryUpdate(BaseModel):
    success: bool