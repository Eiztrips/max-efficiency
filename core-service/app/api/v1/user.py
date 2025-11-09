from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ... import models
from ...schemas import UserRead, UserCreate
from ...database import get_db
from ...services import UserService

router = APIRouter(prefix="/v1/users", tags=["users"])


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)


@router.get("", response_model=List[UserRead])
async def get_users(
    db: AsyncSession = Depends(get_db)
):
    """Получить всех пользователей (DEBUG)"""
    result = await db.execute(select(models.User))
    users = result.scalars().all()
    return users


@router.get("/{max_id}", response_model=UserRead)
async def get_user(
    max_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """
    Получить пользователя по max_id
    """
    user = await user_service.get_user_by_max_id(max_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с max_id={max_id} не найден"
        )
    return user


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """Создать или получить существующего пользователя"""
    return await user_service.get_or_create_user(
        max_id=user_data.max_id,
        username=user_data.username
    )


@router.patch("/{max_id}", response_model=UserRead)
async def update_user(
    max_id: int,
    user_data: dict,
    user_service: UserService = Depends(get_user_service)
):
    """Обновить данные пользователя"""
    user = await user_service.patch_user(max_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с max_id={max_id} не найден"
        )
    return user