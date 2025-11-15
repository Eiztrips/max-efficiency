from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ... import models
from ...schemas import TaskRead, TaskCreate
from ...database import get_db
from ...schemas.ai import APIInputRequest
from ...schemas.task import TaskQuery, TaskUpdate, TaskCreate, TaskCreateRequest
from ...services import TaskService, UserService

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_service(db: AsyncSession = Depends(get_db)) -> TaskService:
    return TaskService(db)

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)

# --------------- DEBUG: Получить все таски ----------------

@router.get("/debug", response_model=List[TaskRead])
async def get_tasks(
    db: AsyncSession = Depends(get_db)
):
    """Получить все таски (DEBUG)"""
    from sqlalchemy.orm import selectinload

    stmt = select(models.Task).options(
        selectinload(models.Task.tags),
        selectinload(models.Task.category),
    )
    result = await db.execute(stmt)
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
    user_id = await user_service.map_max_user_id_to_user_id(max_user_id)
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
    tasks = await task_service.get_tasks(payload)
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

@router.post("/generate", status_code=status.HTTP_202_ACCEPTED)
async def generate_task(
    payload: APIInputRequest,
    task_service: TaskService = Depends(get_task_service)
):
    """
    Сгенерировать задачу с помощью AI
    """
    await task_service.generate_task(payload)

@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreateRequest,
    task_service: TaskService = Depends(get_task_service)
):
    """
    Создать задачу
    """
    user_id = await user_service.map_max_user_id_to_user_id(payload.max_user_id)
    task_create = TaskCreate(
        user_id=user_id,
        title=payload.title,
        description=payload.description,
        expiration_date=payload.expiration_date,
        is_completed=payload.is_completed,
        category_id=payload.category_id
    )
    task = await task_service.create(task_create)
    return TaskRead.model_validate(task)

# --------------- UPDATE ----------------

@router.patch("/{id}", response_model=TaskRead)
async def update_task(
    id: int,
    payload: dict,
    task_service: TaskService = Depends(get_task_service)
):
    """
    Обновить задачу по ID
    """
    from ...schemas.task import TaskUpdate
    task_update = TaskUpdate(id=id, **payload)
    task = await task_service.patch(task_update)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Задача с ID={id} не найдена"
        )
    return TaskRead.model_validate(task)

@router.put("/{task_id}/tags", response_model=TaskRead)
async def update_task_tags(
    task_id: int,
    tag_ids: List[int],
    task_service: TaskService = Depends(get_task_service)
):
    """
    Обновить теги задачи
    """
    task = await task_service.update_task_tags(task_id, tag_ids)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Задача с ID={task_id} не найдена"
        )
    return TaskRead.model_validate(task)

# --------------- UPDATE ----------------

@router.patch("/{id}", response_model=TaskRead)
async def update_task(
    id: int,
    payload: TaskUpdate,
    task_service: TaskService = Depends(get_task_service)
):
    """
    Обновить задачу по ID
    """
    payload.id = id
    updated_task = await task_service.patch(payload)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Задача с ID={id} не найдена"
        )
    return TaskRead.model_validate(updated_task)

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