from datetime import datetime
from pydantic import BaseModel
from typing import Optional

# --------------- REQUEST -------------------

class UserCreate(BaseModel):
    max_user_id: int
    username: Optional[str] = None

# --------------- RESPONSE -------------------

class UserRead(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True