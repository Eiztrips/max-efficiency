from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class TagBase(BaseModel):
    category_id: int
    name: str
    color: Optional[str] = "#FFFFFF"

class TagCreate(TagBase):
    pass

class TagRead(TagBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True