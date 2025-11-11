from datetime import datetime
from pydantic import BaseModel
from typing import Optional

# --------------- REQUEST -------------------

class TagCreate(BaseModel):
    category_id: int
    name: str
    color: Optional[str] = "#FFFFFF"

# --------------- RESPONSE -------------------

class TagRead(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True