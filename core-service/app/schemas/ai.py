from pydantic import BaseModel
from typing import Optional

# --------------- REQUEST -------------------

class APIInputRequest(BaseModel):
    max_user_id: int
    prompt: str
    category_id: int

class TaskInputRequest(BaseModel):
    max_user_id: int
    title: str
    description: Optional[str] = None
    category_id: int
    expiration_date: Optional[str] = None


class InputMessage(BaseModel):
    task_id: str = None # Генерируется в процессе обработки
    prompt: str
    tags: Optional[list[str]] = None
    categories: Optional[list[str]] = None

# --------------- RESPONSE -------------------

class Task(BaseModel):
    title: str
    description: str
    tags: list[str]
    expiration_date: Optional[str] = None
    category: str

class OutputMessage(BaseModel):
    task_id: str
    prompt: str
    task: Task
    model: str
    timestamp: str

# ---------------- REDIS --------------------

class RedisTaskMessage(BaseModel):
    task_id: str
    user_id: int
    category_id: Optional[int] = None