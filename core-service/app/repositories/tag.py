from typing import Optional

from sqlalchemy import select, Sequence
from sqlalchemy.orm import selectinload

from .base import BaseRepository
from ..models import Tag, Task, Category
from ..schemas import TagCreate, TagUpdate


class TagRepository(BaseRepository):

    # --------------- GET ----------------

    async def get_by_id(self, id: int) -> Optional[Tag]:
        result = await self.session.execute(
            select(Tag)
            .options(selectinload(Tag.tasks))
            .where(Tag.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Tag]:
        result = await self.session.execute(select(Tag)
                                            .where(Tag.name == name))
        return result.scalar_one_or_none()

    async def get_tasks(self, tag_id: int) -> Sequence[Task]:
        result = await self.session.execute(
            select(Tag)
            .where(Tag.id == tag_id)
            .options(selectinload(Tag.tasks))
        )
        tag = result.scalar_one_or_none()
        if tag is None:
            return []
        return tag.tasks

    async def get_by_category_id(self, category_id: int) -> Sequence[Tag]:
        result = await self.session.execute(
            select(Tag)
            .where(Tag.category_id == category_id)
        )
        return result.scalars().all()

    async def get_by_user_id(self, user_id: int) -> Sequence[Tag]:
        result = await self.session.execute(
            select(Tag)
            .join(Tag.category)
            .where(Category.owner_id == user_id)
        )
        return result.scalars().all()

    # --------------- CREATE ----------------

    async def create(self, payload: TagCreate) -> Optional[Tag]:
        tag = Tag(
            category_id=payload.category_id,
            name=payload.name,
            color=payload.color
        )
        self.session.add(tag)
        await self.session.commit()
        await self.session.refresh(tag, ['tasks'])
        return tag

    # --------------- UPDATE ----------------

    async def patch(self, payload: TagUpdate) -> Optional[Tag]:
        tag = await self.get_by_id(payload.id)

        if not tag:
            return None

        for k, v in payload.model_dump().items():
            if hasattr(tag, k) and k != "id" and v is not None:
                setattr(tag, k, v)

        self.session.add(tag)
        await self.session.commit()
        await self.session.refresh(tag, ['tasks'])
        return tag

    # --------------- DELETE ----------------

    async def delete(self, id: int) -> bool:
        tag = await self.get_by_id(id)

        if not tag:
            return False

        await self.session.delete(tag)
        await self.session.commit()
        return True

    # --------------- DEBUG ----------------

    async def get_all_tags(self) -> Sequence[Tag]:
        result = await self.session.execute(select(Tag))
        return result.scalars().all()