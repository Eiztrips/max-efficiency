from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ... import models
from ...schemas import UserRead, UserCreate, CategoryRead, TagRead, TaskRead
from ...database import get_db
from ...services import UserService

router = APIRouter(prefix="/v1/users", tags=["users"])


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)

# --------------- DEBUG: Получить всех пользователей ----------------

@router.get("", response_model=List[UserRead])
async def get_users(
    db: AsyncSession = Depends(get_db)
):
    """Получить всех пользователей (DEBUG)"""
    result = await db.execute(select(models.User))
    users = result.scalars().all()
    return users

# --------------- GET ----------------

@router.get("/{max_user_id}", response_model=UserRead)
async def get_user(
    max_user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """
    Получить пользователя по max_user_id
    """
    user = await user_service.get_by_max_user_id(max_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с max_user_id={max_user_id} не найден"
        )
    return user

@router.get("/user/{id}/categories", response_model=List[CategoryRead])
async def get_user_categories(
    id: int,
    user_service: UserService = Depends(get_user_service)
):
    """Получить все категории пользователя по max_user_id"""
    categories = await user_service.get_categories(id)
    return categories

@router.get("/user/{id}/tags", response_model=List[TagRead])
async def get_user_tags(
    id: int,
    user_service: UserService = Depends(get_user_service)
):
    """Получить все теги пользователя по max_user_id"""
    tags = await user_service.get_tags(id)
    return tags

@router.get("/user/{id}/tasks", response_model=List[TaskRead])
async def get_user_tasks(
    id: int,
    user_service: UserService = Depends(get_user_service)
):
    """Получить все задачи пользователя по max_user_id"""
    tasks = await user_service.get_tasks(id)
    return tasks

# --------------- CREATE ----------------

@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """Создать или получить существующего пользователя"""
    return await user_service.get_or_create_user(
        max_user_id=user_data.max_user_id,
        username=user_data.username
    )

# --------------- UPDATE ----------------

@router.patch("/{max_user_id}", response_model=UserRead)
async def update_user(
    max_user_id: int,
    user_data: dict,
    user_service: UserService = Depends(get_user_service)
):
    """Обновить данные пользователя"""
    user = await user_service.patch(max_user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с max_user_id={max_user_id} не найден"
        )
    return user