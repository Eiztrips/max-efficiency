from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ... import models
from ...schemas import TaskRead, TaskCreate
from ...database import get_db
from ...schemas.task import TaskQuery
from ...services import TaskService, UserService

router = APIRouter(prefix="/v1/tasks", tags=["tasks"])


def get_task_service(db: AsyncSession = Depends(get_db)) -> TaskService:
    return TaskService(db)

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)

# --------------- DEBUG: Получить все таски ----------------

@router.get("/", response_model=List[TaskRead])
async def get_tasks(
    db: AsyncSession = Depends(get_db)
):
    """Получить все таски (DEBUG)"""
    result = await db.execute(select(models.Task))
    tasks = result.scalars().all()
    return tasks

# --------------- GET ----------------

@router.get("", response_model=List[TaskRead])
async def get_tasks(
    max_user_id: int,
    category_id: int = None,
    tag_id: int = None,
    status: str = None,
    is_completed: bool = None,
    from_date: str = None,
    to_date: str = None,
    search: str = None,
    task_service: TaskService = Depends(get_task_service),
    user_service: UserService = Depends(get_user_service)
):
    """
    Получить задачи с фильтрацией
    :query max_user_id: max_user_id пользователя
    :query category_id: ID категории для фильтрации
    :query tag_id: ID тега для фильтрации
    :query status: статус задачи ("done" или "pending")
    :query is_completed: флаг завершенности задачи
    :query from_date: дата начала для фильтрации (ISO формат)
    :query to_date: дата окончания для фильтрации (ISO формат)
    :query search: поисковый запрос по заголовку и описанию задачи
    """
    user_id = user_service.map_max_user_id_to_user_id(max_user_id)
    payload = TaskQuery(
        user_id=user_id,
        category_id=category_id,
        tag_id=tag_id,
        status=status,
        is_completed=is_completed,
        from_date=from_date,
        to_date=to_date,
        search=search
    )
    tasks = await task_service.get_tasks(payload=payload)
    return [TaskRead.model_validate(task) for task in tasks]

@router.get("/{id}", response_model=TaskRead)
async def get_task(
    id: int,
    task_service: TaskService = Depends(get_task_service)
):
    """
    Получить задачу по ID
    """
    task = await task_service.get_by_id(id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Задача с ID={id} не найдена"
        )
    return TaskRead.model_validate(task)

# --------------- CREATE ----------------

@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_create: TaskCreate,
    task_service: TaskService = Depends(get_task_service)
):
    """
    Создать новую задачу
    """
    task = await task_service.create(task_create)
    return task
    # TODO: Создание задачке через ИИшку

# --------------- DELETE ----------------

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    id: int,
    task_service: TaskService = Depends(get_task_service)
):
    """
    Удалить задачу по ID
    """
    success = await task_service.delete(id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Задача с ID={id} не найдена"
        )