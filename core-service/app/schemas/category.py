from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class CategoryBase(BaseModel):
    user_id: int
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    user_id: int

class CategoryRead(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class CategoryUpdate(BaseModel):
    success: bool