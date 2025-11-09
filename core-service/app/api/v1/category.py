from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ... import models
from ...schemas import UserRead, UserCreate, CategoryRead, CategoryCreate, TagRead, TaskRead, CategoryUpdate
from ...database import get_db
from ...services import CategoryService

router = APIRouter(prefix="/v1/categories", tags=["categories"])


def get_category_service(db: AsyncSession = Depends(get_db)) -> CategoryService:
    return CategoryService(db)

# --------------- DEBUG: Получить все категории ----------------

@router.get("", response_model=List[CategoryRead])
async def get_categories(
    db: AsyncSession = Depends(get_db)
):
    """Получить все категории (DEBUG)"""
    result = await db.execute(select(models.Category))
    categories = result.scalars().all()
    return categories

# --------------- GET ----------------

@router.get("/{id}", response_model=CategoryRead)
async def get_category(
    id: int,
    category_service: CategoryService = Depends(get_category_service)
):
    """
    Получить категорию по ID
    """
    category = await category_service.get_by_id(id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Категория с ID={id} не найдена"
        )
    return category

@router.get("/{id}/users", response_model=List[UserRead])
async def get_category_users(
    id: int,
    category_service: CategoryService = Depends(get_category_service)
):
    """Получить всех пользователей категории по ID категории"""
    users = await category_service.get_users_by_category_id(id)
    return users

@router.get("/{id}/tags", response_model=List[TagRead])
async def get_category_tags(
    id: int,
    category_service: CategoryService = Depends(get_category_service)
):
    """Получить все теги категории по ID категории"""
    tags = await category_service.get_tags_by_category_id(id)
    return tags

@router.get("/{id}/tasks", response_model=List[TaskRead])
async def get_category_tasks(
    id: int,
    category_service: CategoryService = Depends(get_category_service)
):
    """Получить все задачи категории по ID категории"""
    tasks = await category_service.get_tasks_by_category_id(id)
    return tasks

# --------------- CREATE ----------------

@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_create: CategoryCreate,
    category_service: CategoryService = Depends(get_category_service)
):
    """Создать новую категорию"""
    category = await category_service.create(
        user_id=category_create.user_id,
        name=category_create.name,
        description=category_create.description
    )
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось создать категорию"
        )
    return category

# --------------- UPDATE ----------------

@router.patch("/{category_id}/users/{user_id}", response_model=CategoryUpdate)
async def add_user_to_category(
    category_id: int,
    user_id: int,
    category_service: CategoryService = Depends(get_category_service)
):
    """Добавить пользователя в категорию"""
    category = await category_service.add_user(category_id, user_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось добавить пользователя в категорию"
        )
    return category

# --------------- DELETE ----------------

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    id: int,
    category_service: CategoryService = Depends(get_category_service)
):
    """Удалить категорию по ID"""
    success = await category_service.delete(id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Категория с ID={id} не найдена"
        )
    return None