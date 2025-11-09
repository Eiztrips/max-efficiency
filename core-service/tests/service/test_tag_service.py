import pytest
from app.services.tag import TagService
from app.models import User, Category, Tag, Task


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
        tag = await service.create(category.id, "Test Tag", "#FF0000")

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
        tag = await service.create(category.id, "Test Tag")

        assert tag is not None
        assert tag.color == "#FFFFFF"

    @pytest.mark.asyncio
    async def test_create_invalid_category_id(self, db_session):
        """Тест создания тега с невалидным ID категории"""
        service = TagService(db_session)

        with pytest.raises(ValueError, match="ID категории должен быть положительным целым числом"):
            await service.create(-1, "Test Tag")

        with pytest.raises(ValueError, match="ID категории должен быть положительным целым числом"):
            await service.create(0, "Test Tag")

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

        with pytest.raises(ValueError, match="название тега должен быть непустой строкой"):
            await service.create(category.id, "")

        with pytest.raises(ValueError, match="название тега должен быть непустой строкой"):
            await service.create(category.id, "   ")

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
        tag = await service.create(category.id, "Old Name", "#000000")

        updated_tag = await service.patch(tag.id, {"name": "New Name"})

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
        tag = await service.create(category.id, "Test Tag", "#000000")

        updated_tag = await service.patch(tag.id, {"color": "#FFFFFF"})

        assert updated_tag is not None
        assert updated_tag.name == "Test Tag"
        assert updated_tag.color == "#FFFFFF"

    @pytest.mark.asyncio
    async def test_patch_invalid_id(self, db_session):
        """Тест обновления тега с невалидным ID"""
        service = TagService(db_session)

        with pytest.raises(ValueError, match="ID тега должен быть положительным целым числом"):
            await service.patch(-1, {"name": "New Name"})

        with pytest.raises(ValueError, match="ID тега должен быть положительным целым числом"):
            await service.patch(0, {"name": "New Name"})

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
        tag = await service.create(category.id, "Test Tag")

        with pytest.raises(ValueError, match="данные для обновления тега должен быть непустым словарем"):
            await service.patch(tag.id, {})

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
        tag = await service.create(category.id, "Test Tag")

        with pytest.raises(ValueError, match="Нельзя изменять поле: id"):
            await service.patch(tag.id, {"id": 999})

        with pytest.raises(ValueError, match="Нельзя изменять поле: category_id"):
            await service.patch(tag.id, {"category_id": 999})

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
        tag = await service.create(category.id, "Test Tag")

        result = await service.delete(tag.id)

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_not_found(self, db_session):
        """Тест удаления несуществующего тега"""
        service = TagService(db_session)
        result = await service.delete(999)

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_invalid_id(self, db_session):
        """Тест удаления тега с невалидным ID"""
        service = TagService(db_session)

        with pytest.raises(ValueError, match="ID тега должен быть положительным целым числом"):
            await service.delete(-1)

        with pytest.raises(ValueError, match="ID тега должен быть положительным целым числом"):
            await service.delete(0)

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
        tag = await service.create(category.id, "Test Tag")

        result = await service.get_tasks_by_tag_id(tag.id)

        assert len(result) == 1
        assert result[0].id == tag.id

    @pytest.mark.asyncio
    async def test_get_all_tasks_by_tag_id_invalid_id(self, db_session):
        """Тест получения задач с невалидным ID тега"""
        service = TagService(db_session)

        with pytest.raises(ValueError, match="ID тега должен быть положительным целым числом"):
            await service.get_tasks_by_tag_id(-1)

        with pytest.raises(ValueError, match="ID тега должен быть положительным целым числом"):
            await service.get_tasks_by_tag_id(0)

