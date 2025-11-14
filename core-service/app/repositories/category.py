from typing import Optional

from sqlalchemy import select, Sequence
from sqlalchemy.orm import selectinload

from .base import BaseRepository
from ..models import Category, User, Tag, Task
from ..schemas import CategoryCreate, CategoryUpdate, CategoryUsersUpdateV2


class CategoryRepository(BaseRepository):

    # --------------- GET ----------------

    async def get_by_id(self, id: int) -> Optional[Category]:
        result = await self.session.execute(
            select(Category)
            .options(
                selectinload(Category.users),
                selectinload(Category.tags),
                selectinload(Category.tasks)
            )
            .where(Category.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> Sequence[Category]:
        result = await self.session.execute(
            select(Category)
            .options(
                selectinload(Category.users),
                selectinload(Category.tags),
                selectinload(Category.tasks)
            )
            .where(Category.owner_id == user_id)
        )
        return result.scalars().all()

    async def get_joined_users(self, category_id: int) -> Sequence[User]:
        result = await self.session.execute(
            select(User)
            .options(
                selectinload(User.categories_owned),
                selectinload(User.categories_joined)
            )
            .join(Category.users)
            .where(Category.id == category_id)
        )
        return result.scalars().all()

    async def get_tags(self, category_id: int) -> Sequence[Tag]:
        result = await self.session.execute(
            select(Tag)
            .options(selectinload(Tag.tasks))
            .where(Tag.category_id == category_id)
        )
        return result.scalars().all()

    async def get_tasks(self, category_id: int) -> Sequence[Task]:
        from ..models import Task
        result = await self.session.execute(
            select(Task)
            .options(selectinload(Task.tags))
            .where(Task.category_id == category_id)
        )
        return result.scalars().all()

    async def get_id_by_name_and_owner(self, name: str, owner_id: int) -> Optional[int]:
        result = await self.session.execute(
            select(Category.id)
            .where(Category.name == name)
            .where(Category.owner_id == owner_id)
        )
        category_id = result.scalar_one_or_none()
        return category_id

    # --------------- CREATE ----------------

    async def update(self, payload: CategoryUpdate) -> Category:
        category = await self.get_by_id(payload.id)
        if not category:
            raise ValueError(f"Category with ID={payload.id} not found")
        for key, value in payload.model_dump().items():
            if value is not None and key != "id":
                setattr(category, key, value)
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category, ['users', 'tags', 'tasks'])
        return category

    async def create(self, payload: CategoryCreate) -> Optional[Category]:
        category = Category(
            owner_id=payload.user_id,
            name=payload.name,
            description=payload.description
        )
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category, ['users', 'tags', 'tasks'])
        return category

    # --------------- UPDATE ----------------

    async def patch(self, payload: CategoryUpdate) -> bool:
        category = await self.get_by_id(payload.id)
        if not category:
            return False
        for key, value in payload.model_dump().items():
            if value is not None and key != "id":
                setattr(category, key, value)
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category, ['users', 'tags', 'tasks'])
        return True

    async def add_user(self, payload: CategoryUsersUpdateV2) -> bool:
        category = await self.get_by_id(payload.id)
        if not category: return False
        user = await self.session.get(User, payload.user_id)
        if not user: return False
        category.users.append(user)
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category, ['users', 'tags', 'tasks'])
        return True

    async def remove_user(self, payload: CategoryUsersUpdateV2) -> bool:
        category = await self.get_by_id(payload.id)
        if not category: return False
        user = await self.session.get(User, payload.user_id)
        if not user: return False
        if user in category.users:
            category.users.remove(user)
            self.session.add(category)
            await self.session.commit()
            await self.session.refresh(category, ['users', 'tags', 'tasks'])
        return True


    # --------------- DELETE ----------------

    async def delete(self, id: int) -> bool:
        category = await self.get_by_id(id)
        if not category:
            return False
        await self.session.delete(category)
        await self.session.commit()
        return True

    # --------------- для DEBUG жеск ----------------

    async def get_all_categories(self, offset_: int = 0, limit_: int = 100) -> Sequence[Category]:
        result = await self.session.execute(
            select(Category)
            .options(
                selectinload(Category.users),
                selectinload(Category.tags),
                selectinload(Category.tasks)
            )
            .offset(offset_)
            .limit(limit_)
        )
        return result.scalars().all()
