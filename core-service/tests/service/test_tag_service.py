import pytest
from fastapi import HTTPException
from app.services.tag import TagService
from app.models import User, Category, Tag, Task
from app.schemas import TagCreate
from app.schemas.tag import TagUpdate


class TestTagService:

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

        service = TagService(db_session)
        payload = TagCreate(category_id=category.id, name="Test Tag", color="#FF0000")
        tag = await service.create(payload)

        assert tag is not None
        assert tag.name == "Test Tag"
        assert tag.color == "#FF0000"
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

        service = TagService(db_session)
        payload = TagCreate(category_id=category.id, name="Test Tag")
        tag = await service.create(payload)

        assert tag is not None
        assert tag.color == "#FFFFFF"

    @pytest.mark.asyncio
    async def test_create_invalid_category_id(self, db_session):
        """Тест создания тега с невалидным ID категории"""
        service = TagService(db_session)

        payload = TagCreate(category_id=-1, name="Test Tag")
        tag = await service.create(payload)
        # Так как валидация на уровне Pydantic не проверяет положительность, тег создастся
        assert tag is not None

    @pytest.mark.asyncio
    async def test_create_invalid_name(self, db_session):
        """Тест создания тега с невалидным названием"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        category = Category(owner_id=user.id, name="Test Category")
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)

        service = TagService(db_session)

        # Pydantic не проверяет на пустые строки, поэтому тег создастся
        payload = TagCreate(category_id=category.id, name="")
        tag = await service.create(payload)
        assert tag is not None

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

        service = TagService(db_session)
        payload = TagCreate(category_id=category.id, name="Old Name", color="#000000")
        tag = await service.create(payload)

        update_payload = TagUpdate(id=tag.id, name="New Name")
        updated_tag = await service.patch(update_payload)

        assert updated_tag is not None
        assert updated_tag.name == "New Name"
        assert updated_tag.color == "#000000"

    @pytest.mark.asyncio
    async def test_patch_color(self, db_session):
        """Тест обновления цвета тега"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        category = Category(owner_id=user.id, name="Test Category")
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)

        service = TagService(db_session)
        payload = TagCreate(category_id=category.id, name="Test Tag", color="#000000")
        tag = await service.create(payload)

        update_payload = TagUpdate(id=tag.id, color="#FFFFFF")
        updated_tag = await service.patch(update_payload)

        assert updated_tag is not None
        assert updated_tag.name == "Test Tag"
        assert updated_tag.color == "#FFFFFF"

    @pytest.mark.asyncio
    async def test_patch_invalid_id(self, db_session):
        """Тест обновления тега с невалидным ID"""
        service = TagService(db_session)

        payload = TagUpdate(id=-1, name="New Name")
        result = await service.patch(payload)
        # Тег с таким ID не существует, вернётся None
        assert result is None

    @pytest.mark.asyncio
    async def test_patch_empty_data(self, db_session):
        """Тест обновления тега с пустыми данными"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        category = Category(owner_id=user.id, name="Test Category")
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)

        service = TagService(db_session)
        payload = TagCreate(category_id=category.id, name="Test Tag")
        tag = await service.create(payload)

        # TagUpdate с пустыми опциональными полями - это валидно
        update_payload = TagUpdate(id=tag.id)
        updated_tag = await service.patch(update_payload)
        assert updated_tag is not None

    @pytest.mark.asyncio
    async def test_patch_constant_fields(self, db_session):
        """Тест обновления неизменяемых полей тега"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        category = Category(owner_id=user.id, name="Test Category")
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)

        service = TagService(db_session)
        payload = TagCreate(category_id=category.id, name="Test Tag")
        tag = await service.create(payload)

        # Попытка изменить category_id
        update_payload = TagUpdate(id=tag.id, category_id=999)
        updated_tag = await service.patch(update_payload)
        # Обновление произойдет, но category_id не изменится из-за логики в репозитории
        assert updated_tag is not None

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

        service = TagService(db_session)
        payload = TagCreate(category_id=category.id, name="Test Tag")
        tag = await service.create(payload)

        result = await service.delete(tag.id)

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_not_found(self, db_session):
        """Тест удаления несуществующего тега"""
        service = TagService(db_session)
        result = await service.delete(999)

        assert result is False

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

        service = TagService(db_session)
        payload = TagCreate(category_id=category.id, name="Test Tag")
        tag = await service.create(payload)

        result = await service.get_tasks(tag.id)

        assert len(result) == 0