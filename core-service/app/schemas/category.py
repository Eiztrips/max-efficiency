from datetime import datetime
from pydantic import BaseModel
from typing import Optional


# --------------- REQUEST -------------------

class CategoryCreate(BaseModel):
    user_id: int
    name: str
    description: Optional[str] = None

class CategoryUpdate(BaseModel):
    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    owner_id: Optional[int] = None

class CategoryUsersUpdate(BaseModel):
    id: int
    user_id: int

# --------------- RESPONSE -------------------

class CategoryRead(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True