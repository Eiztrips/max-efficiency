import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.repositories.tag import TagRepository
from app.models import User, Category, Tag, Task
from app.schemas import TagCreate
from app.schemas.tag import TagUpdate


class TestTagRepository:

    @pytest.mark.asyncio
    async def test_get_by_id(self, db_session):
        """Тест получения тега по ID"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        category = Category(owner_id=user.id, name="Test Category")
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)

        repo = TagRepository(db_session)
        payload = TagCreate(category_id=category.id, name="Test Tag", color="#FF0000")
        tag = await repo.create(payload)
        result = await repo.get_by_id(tag.id)

        assert result is not None
        assert result.id == tag.id
        assert result.name == "Test Tag"
        assert result.color == "#FF0000"
        assert result.category_id == category.id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, db_session):
        """Тест получения несуществующего тега"""
        repo = TagRepository(db_session)
        result = await repo.get_by_id(999)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_name(self, db_session):
        """Тест получения тега по имени"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        category = Category(owner_id=user.id, name="Test Category")
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)

        repo = TagRepository(db_session)
        payload = TagCreate(category_id=category.id, name="Unique Tag")
        tag = await repo.create(payload)
        result = await repo.get_by_name("Unique Tag")

        assert result is not None
        assert result.id == tag.id
        assert result.name == "Unique Tag"

    @pytest.mark.asyncio
    async def test_get_by_name_not_found(self, db_session):
        """Тест получения несуществующего тега по имени"""
        repo = TagRepository(db_session)
        result = await repo.get_by_name("Nonexistent Tag")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_category_id(self, db_session):
        """Тест получения всех тегов категории"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        category = Category(owner_id=user.id, name="Test Category")
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)

        repo = TagRepository(db_session)
        payload1 = TagCreate(category_id=category.id, name="Tag 1")
        tag1 = await repo.create(payload1)
        payload2 = TagCreate(category_id=category.id, name="Tag 2")
        tag2 = await repo.create(payload2)

        result = await repo.get_by_category_id(category.id)

        assert len(result) == 2
        assert tag1 in result
        assert tag2 in result

    @pytest.mark.asyncio
    async def test_get_by_category_id_empty(self, db_session):
        """Тест получения тегов несуществующей категории"""
        repo = TagRepository(db_session)
        result = await repo.get_by_category_id(999)

        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_all_tasks_by_tag_id(self, db_session):
        """Тест получения всех задач по ID тега"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        category = Category(owner_id=user.id, name="Test Category")
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)

        repo = TagRepository(db_session)
        payload = TagCreate(category_id=category.id, name="Test Tag")
        tag = await repo.create(payload)

        task1 = Task(user_id=user.id, title="Task 1", category_id=category.id)
        task2 = Task(user_id=user.id, title="Task 2", category_id=category.id)
        db_session.add(task1)
        db_session.add(task2)
        await db_session.commit()
        await db_session.refresh(task1)
        await db_session.refresh(task2)

        tag_obj = await db_session.scalar(
            select(Tag).options(selectinload(Tag.tasks)).where(Tag.id == tag.id)
        )
        tag_obj.tasks.append(task1)
        tag_obj.tasks.append(task2)
        db_session.add(tag_obj)
        await db_session.commit()

        result = await repo.get_tasks(tag.id)

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_create(self, db_session):
        """Тест создания тега"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        category = Category(owner_id=user.id, name="Test Category")
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)

        repo = TagRepository(db_session)
        payload = TagCreate(category_id=category.id, name="New Tag", color="#00FF00")
        tag = await repo.create(payload)

        assert tag is not None
        assert tag.name == "New Tag"
        assert tag.color == "#00FF00"
        assert tag.category_id == category.id

    @pytest.mark.asyncio
    async def test_create_with_default_color(self, db_session):
        """Тест создания тега с цветом по умолчанию"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        category = Category(owner_id=user.id, name="Test Category")
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)

        repo = TagRepository(db_session)
        payload = TagCreate(category_id=category.id, name="New Tag")
        tag = await repo.create(payload)

        assert tag is not None
        assert tag.color == "#FFFFFF"

    @pytest.mark.asyncio
    async def test_patch(self, db_session):
        """Тест обновления тега"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        category = Category(owner_id=user.id, name="Test Category")
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)

        repo = TagRepository(db_session)
        payload = TagCreate(category_id=category.id, name="Old Name", color="#000000")
        tag = await repo.create(payload)

        update_payload = TagUpdate(id=tag.id, name="New Name", color="#FFFFFF")
        updated_tag = await repo.patch(update_payload)

        assert updated_tag is not None
        assert updated_tag.id == tag.id
        assert updated_tag.name == "New Name"
        assert updated_tag.color == "#FFFFFF"

    @pytest.mark.asyncio
    async def test_patch_not_found(self, db_session):
        """Тест обновления несуществующего тега"""
        repo = TagRepository(db_session)
        payload = TagUpdate(id=999, name="New Name")
        result = await repo.patch(payload)

        assert result is None

    @pytest.mark.asyncio
    async def test_delete(self, db_session):
        """Тест удаления тега"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        category = Category(owner_id=user.id, name="Test Category")
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)

        repo = TagRepository(db_session)
        payload = TagCreate(category_id=category.id, name="Tag to Delete")
        tag = await repo.create(payload)

        result = await repo.delete(tag.id)

        assert result is True
        deleted_tag = await repo.get_by_id(tag.id)
        assert deleted_tag is None

    @pytest.mark.asyncio
    async def test_delete_not_found(self, db_session):
        """Тест удаления несуществующего тега"""
        repo = TagRepository(db_session)
        result = await repo.delete(999)

        assert result is False

    @pytest.mark.asyncio
    async def test_get_all_tags(self, db_session):
        """Тест получения всех тегов"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        category = Category(owner_id=user.id, name="Test Category")
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)

        repo = TagRepository(db_session)
        payload1 = TagCreate(category_id=category.id, name="Tag 1")
        tag1 = await repo.create(payload1)
        payload2 = TagCreate(category_id=category.id, name="Tag 2")
        tag2 = await repo.create(payload2)

        result = await repo.get_all_tags()

        assert len(result) == 2
        assert tag1 in result
        assert tag2 in result

        result = await repo.get_all_tags()

        assert len(result) == 2
        assert tag1 in result
        assert tag2 in result

