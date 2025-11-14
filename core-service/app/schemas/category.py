from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import Optional


# --------------- REQUEST -------------------

class APICategoryCreate(BaseModel):
    max_user_id: int
    name: str
    description: Optional[str] = None

class CategoryCreate(BaseModel):
    user_id: int
    name: str
    description: Optional[str] = None

class CategoryUpdate(BaseModel):
    id: int = None
    name: Optional[str] = None
    description: Optional[str] = None
    owner_id: Optional[int] = None

class CategoryUsersUpdate(BaseModel):
    id: int
    max_user_id: int

class CategoryUsersUpdateV2(BaseModel):
    id: int
    user_id: int

# --------------- RESPONSE -------------------

class CategoryRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    owner_id: int

    joined_users: Optional[list[int]] = []
    tags: Optional[list[int]] = []
    tasks: Optional[list[int]] = []

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_validator('joined_users', 'tags', 'tasks', mode='before')
    @classmethod
    def extract_ids(cls, value):
        if value is None:
            return []
        if isinstance(value, list):
            return [item.id if hasattr(item, 'id') else item for item in value]
        return value
