from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ... import models
from ...schemas import TagRead, TaskRead, TagCreate
from ...database import get_db
from ...services import TagService

router = APIRouter(prefix="/tags", tags=["tags"])


def get_tag_service(db: AsyncSession = Depends(get_db)) -> TagService:
    return TagService(db)

# --------------- DEBUG: Получить все теги ----------------

@router.get("/debug", response_model=List[TagRead])
async def get_tags(
    db: AsyncSession = Depends(get_db)
):
    """Получить все теги (DEBUG)"""
    from sqlalchemy.orm import selectinload

    stmt = select(models.Tag).options(
        selectinload(models.Tag.tasks),
    )
    result = await db.execute(stmt)
    tags = result.scalars().all()
    return [TagRead.model_validate(tag) for tag in tags]

# --------------- GET ----------------

@router.get("/{id}", response_model=TagRead)
async def get_tag(
    id: int,
    tag_service: TagService = Depends(get_tag_service)
):
    """
    Получить тег по ID
    """
    tag = await tag_service.get_by_id(id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тег с ID={id} не найден"
        )
    return TagRead.model_validate(tag)

@router.get("/{id}/tasks", response_model=List[TaskRead])
async def get_tasks(
    id: int,
    tag_service: TagService = Depends(get_tag_service)
):
    """Получить все задачи с данным тегом по ID тега"""
    tasks = await tag_service.get_tasks(id)
    return [TaskRead.model_validate(task) for task in tasks]

# --------------- CREATE ----------------

@router.post("", response_model=TagRead, status_code=status.HTTP_201_CREATED)
async def create_tag(
    payload: TagCreate,
    tag_service: TagService = Depends(get_tag_service)
):
    """
    Создать новый тег
    """
    tag = await tag_service.create(payload)
    return TagRead.model_validate(tag)

# --------------- DELETE ----------------

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    id: int,
    tag_service: TagService = Depends(get_tag_service)
):
    """
    Удалить тег по ID
    """
    success = await tag_service.delete(id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тег с ID={id} не найден"
        )