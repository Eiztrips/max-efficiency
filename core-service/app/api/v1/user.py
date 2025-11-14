from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ... import models
from ...schemas import UserRead, UserCreate, CategoryRead, TagRead, TaskRead, TaskQuery
from ...database import get_db
from ...services import UserService, TaskService

router = APIRouter(prefix="/users", tags=["users"])


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)

def get_task_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)

# --------------- DEBUG: Получить всех пользователей ----------------

@router.get("", response_model=List[UserRead])
async def get_users(
    db: AsyncSession = Depends(get_db)
):
    """Получить всех пользователей (DEBUG)"""
    from sqlalchemy.orm import selectinload

    stmt = select(models.User).options(
        selectinload(models.User.categories_owned),
        selectinload(models.User.categories_joined),
    )
    result = await db.execute(stmt)
    users = result.scalars().all()
    return [UserRead.model_validate(user) for user in users]

# --------------- GET ----------------

@router.get("/{max_user_id}", response_model=UserRead)
async def get_user(
    max_user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """
    Получить пользователя по max_user_id
    """
    user_id = await user_service.map_max_user_id_to_user_id(max_user_id)
    user = await user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с max_user_id={max_user_id} не найден"
        )
    return UserRead.model_validate(user)

@router.get("/user/{max_user_id}/categories", response_model=List[CategoryRead])
async def get_user_categories(
    max_user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """Получить все категории пользователя по max_user_id"""
    user_id = await user_service.map_max_user_id_to_user_id(max_user_id)
    categories = await user_service.get_categories(user_id)
    return [CategoryRead.model_validate(category) for category in categories]

@router.get("/user/{max_user_id}/tags", response_model=List[TagRead])
async def get_user_tags(
    max_user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """Получить все теги пользователя по max_user_id"""
    user_id = await user_service.map_max_user_id_to_user_id(max_user_id)
    tags = await user_service.get_tags(user_id)
    return [TagRead.model_validate(tag) for tag in tags]

@router.get("/user/{max_user_id}/tasks", response_model=List[TaskRead])
async def get_user_tasks(
    max_user_id: int,
    user_service: UserService = Depends(get_user_service),
    task_service: TaskService = Depends(get_task_service)
):
    """Получить все задачи пользователя по max_user_id"""
    user_id = await user_service.map_max_user_id_to_user_id(max_user_id)
    payload = TaskQuery(user_id=user_id)
    tasks = await task_service.get_tasks(payload=payload)
    return [TaskRead.model_validate(task) for task in tasks]

# --------------- CREATE ----------------

@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate = Body(),
    user_service: UserService = Depends(get_user_service)
):
    """Создать или получить существующего пользователя"""
    response = await user_service.get_or_create(payload)
    return UserRead.model_validate(response)

# --------------- UPDATE ----------------

""" не используется, но пусть будет
@router.patch("/{max_user_id}", response_model=UserRead)
async def update_user(
    max_user_id: int,
    user_data: dict,
    user_service: UserService = Depends(get_user_service)
):
    \"""Обновить данные пользователя\"""
    user_id = await user_service.map_max_user_id_to_user_id(max_user_id)
    user = await user_service.patch(user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с max_user_id={max_user_id} не найден"
        )
    return UserRead.model_validate(user)
"""