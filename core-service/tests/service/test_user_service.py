import pytest
from fastapi import HTTPException

from app.schemas import UserCreate
from app.services.user import UserService
from app.models import Category, Task


class TestUserService:
    """Тесты для UserService"""

    @pytest.mark.asyncio
    async def test_map_max_user_id_to_user_id(self, db_session):
        """Тест маппинга max_user_id на внутренний user_id"""
        service = UserService(db_session)
        payload = UserCreate(max_user_id=123456, username="test_user")
        user = await service.get_or_create(payload)
        user_id = await service.map_max_user_id_to_user_id(123456)
        assert user_id == user.id

    @pytest.mark.asyncio
    async def test_get_user_by_username(self, db_session):
        """Тест получения пользователя по username"""
        service = UserService(db_session)

        payload = UserCreate(max_user_id=123456, username="test_user")
        await service.get_or_create(payload)

        user = await service.get_by_username("test_user")

        assert user is not None
        assert user.username == "test_user"
        assert user.max_user_id == 123456

    @pytest.mark.asyncio
    async def test_get_user_by_username_not_found(self, db_session):
        """Тест получения несуществующего пользователя по username"""
        service = UserService(db_session)

        user = await service.get_by_username("nonexistent_user")

        assert user is None

    @pytest.mark.asyncio
    async def test_get_user_by_username_invalid_value(self, db_session):
        """Тест с невалидным username"""
        service = UserService(db_session)

        with pytest.raises(HTTPException) as exc_info:
            await service.get_by_username("")

        assert exc_info.value.status_code == 400
        assert "username пользователя должен быть непустой строкой" in exc_info.value.detail

        with pytest.raises(HTTPException) as exc_info:
            await service.get_by_username("   ")

        assert exc_info.value.status_code == 400
        assert "username пользователя должен быть непустой строкой" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_or_create_user_creates_new(self, db_session):
        """Тест создания нового пользователя"""
        service = UserService(db_session)

        payload = UserCreate(max_user_id=123456, username="new_user")
        await service.get_or_create(payload)

        user_id = await service.map_max_user_id_to_user_id(123456)
        user = await service.get_by_id(user_id)

        assert user is not None
        assert user.max_user_id == 123456
        assert user.username == "new_user"
        assert user.id is not None

    @pytest.mark.asyncio
    async def test_get_or_create_user_returns_existing(self, db_session):
        """Тест возврата существующего пользователя"""
        service = UserService(db_session)

        user1 = payload = UserCreate(max_user_id=123456, username="test_user")
        await service.get_or_create(payload)

        payload = UserCreate(max_user_id=123456, username="another_name")
        user2 = await service.get_or_create(payload)

        assert user2.max_user_id == 123456
        assert user2.username == "test_user"

    @pytest.mark.asyncio
    async def test_get_user_categories(self, db_session):
        """Тест получения категорий пользователя"""
        service = UserService(db_session)

        payload = UserCreate(max_user_id=123456, username="test_user")
        user = await service.get_or_create(payload)

        category1 = Category(name="Category 1", description="Desc 1", owner_id=user.id)
        category2 = Category(name="Category 2", description="Desc 2", owner_id=user.id)
        db_session.add(category1)
        db_session.add(category2)
        await db_session.commit()

        user_id = await service.map_max_user_id_to_user_id(123456)
        categories = await service.get_categories(user_id)

        assert len(categories) == 2
        assert all(isinstance(c, Category) for c in categories)

    @pytest.mark.asyncio
    async def test_get_user_tasks(self, db_session):
        """Тест получения задач пользователя"""
        service = UserService(db_session)

        payload = UserCreate(max_user_id=123456, username="test_user")
        user = await service.get_or_create(payload)

        category = Category(name="Category", description="Desc", owner_id=user.id)
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)

        task1 = Task(user_id=user.id, title="Task 1", category_id=category.id)
        task2 = Task(user_id=user.id, title="Task 2", category_id=category.id)
        db_session.add(task1)
        db_session.add(task2)
        await db_session.commit()

        user_id = await service.map_max_user_id_to_user_id(123456)
        tasks = await service.get_tasks(user_id)

        assert len(tasks) == 2
        assert all(isinstance(t, Task) for t in tasks)

    @pytest.mark.asyncio
    async def test_get_user_tags(self, db_session):
        """Тест получения тегов пользователя"""
        service = UserService(db_session)

        payload = UserCreate(max_user_id=123456, username="test_user")
        user = await service.get_or_create(payload)

        category = Category(name="Category", description="Desc", owner_id=user.id)
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)

        from app.models import Tag
        tag1 = Tag(name="Tag 1", color="red", category_id=category.id)
        tag2 = Tag(name="Tag 2", color="blue", category_id=category.id)
        db_session.add(tag1)
        db_session.add(tag2)
        await db_session.commit()

        user_id = await service.map_max_user_id_to_user_id(123456)
        tags = await service.get_tags(user_id)

        assert len(tags) == 2
        assert all(isinstance(t, Tag) for t in tags)

