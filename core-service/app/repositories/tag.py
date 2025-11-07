from typing import Optional

from sqlalchemy import select, update, Sequence

from .base import BaseRepository
from app.models.tag import Tag

class TagRepository(BaseRepository):

    # --------------- GET ----------------

    async def get_by_id(self, id: int) -> Optional[Tag]:
        result = await self.session.execute(select(Tag)
                                            .where(Tag.id == id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Tag]:
        result = await self.session.execute(select(Tag)
                                            .where(Tag.name == name))
        return result.scalar_one_or_none()

    async def get_by_category_id(self, category_id: int) -> Sequence[Tag]:
        result = await self.session.execute(
            select(Tag)
            .where(Tag.category_id == category_id)
        )
        return result.scalars().all()

    # --------------- CREATE ----------------

    async def create(self, category_id: int, name: str, color: str = "gray") -> Optional[Tag]:
        tag = Tag(
            category_id=category_id,
            name=name,
            color=color
        )
        self.session.add(tag)
        await self.session.commit()
        await self.session.refresh(tag)
        return tag

    # --------------- UPDATE ----------------

    async def update(self, id: int, data: dict) -> Optional[Tag]:
        result = await self.session.execute(
            update(Tag)
            .where(Tag.id == id)
            .values(**data)
            .returning(Tag)
        )
        await self.session.commit()
        return result.scalar_one_or_none()

    async def patch(self, id: int, data: dict) -> Optional[Tag]:
        tag = await self.get_by_id(id)

        if not tag:
            return None

        for k, v in data.items():
            if hasattr(tag, k):
                setattr(tag, k, v)

        self.session.add(tag)
        await self.session.commit()
        await self.session.refresh(tag)
        return tag

    # --------------- DELETE ----------------

    async def delete(self, id: int) -> bool:
        tag = await self.get_by_id(id)

        if not tag:
            return False

        await self.session.delete(tag)
        await self.session.commit()
        return True

    # --------------- для DEBUG жеск ----------------

    async def get_all_tags(self) -> Sequence[Tag]:
        result = await self.session.execute(select(Tag))
        return result.scalars().all()