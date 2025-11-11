from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import Optional

# --------------- REQUEST -------------------

class UserCreate(BaseModel):
    max_user_id: int
    username: Optional[str] = None

# --------------- RESPONSE -------------------

class UserRead(BaseModel):
    id: int
    max_user_id: int
    username: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    categories_owned: Optional[list[int]] = []
    categories_joined: Optional[list[int]] = []

    model_config = {"from_attributes": True}

    @field_validator("categories_owned", "categories_joined", mode='before')
    @classmethod
    def extract_ids(cls, value):
        if value is None:
            return []
        if isinstance(value, list):
            return [item.id if hasattr(item, 'id') else item for item in value]
        return value