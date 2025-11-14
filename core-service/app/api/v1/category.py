from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ... import models
from ...schemas import UserRead, CategoryRead, CategoryCreate, TagRead, TaskRead
from ...database import get_db
from ...schemas.category import CategoryUsersUpdate, CategoryUsersUpdateV2, APICategoryCreate, CategoryUpdate
from ...services import CategoryService, UserService

router = APIRouter(prefix="/categories", tags=["categories"])


def get_category_service(db: AsyncSession = Depends(get_db)) -> CategoryService:
    return CategoryService(db)

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)

# --------------- DEBUG: Получить все категории ----------------

@router.get("/debug", response_model=List[CategoryRead])
async def get_categories(
    db: AsyncSession = Depends(get_db)
):
    """Получить все категории (DEBUG)"""
    from sqlalchemy.orm import selectinload

    stmt = select(models.Category).options(
        selectinload(models.Category.users),
        selectinload(models.Category.tags),
        selectinload(models.Category.tasks),
    )
    result = await db.execute(stmt)
    categories = result.scalars().all()
    return [CategoryRead.model_validate(category) for category in categories]

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
    return CategoryRead.model_validate(category)

@router.get("/{id}/users", response_model=List[UserRead])
async def get_category_users(
    id: int,
    category_service: CategoryService = Depends(get_category_service)
):
    """Получить всех пользователей категории по ID категории"""
    users = await category_service.get_joined_users(id)
    return [UserRead.model_validate(user) for user in users]

@router.get("/{id}/tags", response_model=List[TagRead])
async def get_category_tags(
    id: int,
    category_service: CategoryService = Depends(get_category_service)
):
    """Получить все теги категории по ID категории"""
    tags = await category_service.get_tags(id)
    return [TaskRead.model_validate(tag) for tag in tags]

@router.get("/{id}/tasks", response_model=List[TaskRead])
async def get_category_tasks(
    id: int,
    category_service: CategoryService = Depends(get_category_service)
):
    """Получить все задачи категории по ID категории"""
    tasks = await category_service.get_tasks(id)
    return [TaskRead.model_validate(task) for task in tasks]

# --------------- CREATE ----------------

@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: APICategoryCreate,
    category_service: CategoryService = Depends(get_category_service),
    user_service: UserService = Depends(get_user_service)
):
    """Создать новую категорию"""
    user_id = await user_service.map_max_user_id_to_user_id(payload.max_user_id)
    category_create = CategoryCreate(
        user_id=user_id,
        name=payload.name.lower(),
        description=payload.description
    )
    category = await category_service.create(category_create)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось создать категорию"
        )
    return CategoryRead.model_validate(category)

# --------------- UPDATE ----------------

@router.patch("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: int,
    payload: CategoryUpdate,
    category_service: CategoryService = Depends(get_category_service)
):
    """Обновить категорию по ID"""
    payload.id = category_id
    category = await category_service.patch(payload)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось обновить категорию"
        )
    return CategoryRead.model_validate(category)

@router.post("/{category_id}/users/{max_user_id}", response_model=CategoryRead)
async def add_user_to_category(
    payload: CategoryUsersUpdate,
    category_service: CategoryService = Depends(get_category_service),
    user_service: UserService = Depends(get_user_service)
):
    """Добавить пользователя в категорию"""
    user_id = await user_service.map_max_user_id_to_user_id(payload.max_user_id)
    payload = CategoryUsersUpdateV2(**{"id": payload.id, "user_id": user_id})
    category = await category_service.add_user(payload)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось добавить пользователя в категорию"
        )
    return CategoryRead.model_validate(category)

@router.delete("/{category_id}/users/{max_user_id}", response_model=CategoryRead)
async def remove_user_from_category(
    category_id: int,
    max_user_id: int,
    category_service: CategoryService = Depends(get_category_service),
    user_service: UserService = Depends(get_user_service)
):
    """Удалить пользователя из категории"""
    user_id = await user_service.map_max_user_id_to_user_id(max_user_id)
    payload = CategoryUsersUpdateV2(**{"id": category_id, "user_id": user_id})
    category = await category_service.remove_user(payload)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось удалить пользователя из категории"
        )
    return CategoryRead.model_validate(category)

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